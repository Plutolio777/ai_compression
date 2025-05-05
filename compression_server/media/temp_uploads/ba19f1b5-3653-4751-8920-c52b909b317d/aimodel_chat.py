# -*- coding: utf-8 -*-
import json
from typing import Iterator, Any

import httpx
from openai import OpenAI
from requests import Response
from requests.models import ITER_CHUNK_SIZE

# from chat import DOU_TOKEN, DOU_URL, DOU_MODEL

# from xenadmin import db, app
# from xenadmin.admin.models import SystemConfig
# from xenadmin.alarm.main_collection_detail import CollectionAlarmInfoManage

QGPT_CONFIG_KEY = 'qgpt_config_key'
DOU_TOKEN = "9f03871d-2b76-468e-82a5-dc370957b35a"
DOU_URL = "https://ark.cn-beijing.volces.com/api/v3"
DOU_MODEL = "deepseek-r1-250120"
validation_mapping = {
    "暂不确定": 4,
    "有效": 3,
    "无效": 2
}
attack_result_mapping = {
    "攻击成功": 3,
    "攻击失败": 2,
    "暂不确定": 1
}
field_desc = {
    "last_access_time": "告警最近发生时间",
    "attacker": "攻击IP",
    "victim": "受害IP",
    "level": "威胁级别，0表示低危，1表示中危，2表示高危，3表示危急",
    "sip": "源IP",
    "dip": "目的IP",
    "sport": "源端口",
    "dport": "目标端口",
    "host": "域名",
    "rule_id": "规则ID，16进制数字",
    "protocol": "协议",
    "xff": "X-Forwarded-For	",
    "threat_name": "威胁名称",
    # "start_time": 1741017600000,
    # "end_time": 1741085898000,
    # "id": "20250304_87bfa04a70c85d7fb3f65e8e4f3e8c46",
    # "sip_ioc_dip": "83cc598ed232a08359247edf3b2345ac",
    # "skyeye_type": "webids-webattack_dolog",
    # "type_chain": "告警类型名编号",
    "ioc": "威胁情报，情报类告警ioc字段才有值",  # 对接GPT的字段中没有这个字段，但还是放在这里
    # "branch_id": "QUlQAPnRS",
    # "gpt_result": 0,
    # "gpt_attack_result": 0,
    "uri": "uri，统一资源标识符",
    "req_param": "请求参数",
    "result": "攻击结果，0表示企图，1表示成功，2表示实现，3表示失败",
    "status_code": "响应状态码",
    "vuln_desc": "漏洞描述",
    "vuln_type": "漏洞类型",
    "payload": "攻击载荷payload（Base64编码）",
    "req_header": "请求头",
    "agent": "user-agent",
    "req_method": "请求方法",
    "req_body": "请求体",
    "rsp_header": "响应头",
    "rsp_body": "响应体"
}


class DeepSeekResponse(Response):

    def __init__(self, raw_response: httpx.Response = None, completions=None):
        super().__init__()
        self.reason = raw_response.reason_phrase
        self.headers = raw_response.headers
        self.encoding = raw_response.encoding
        self.status_code = raw_response.status_code
        self.completions = completions

    @property
    def content(self):
        raw_message = self.completions.choices[0].message.content
        output_dict = {}
        if not raw_message:
            return output_dict
        if "<analysis>" in raw_message and "</analysis>" in raw_message:
            analysis_parts = raw_message.split("</analysis>")
            analysis_content = analysis_parts[0].split("<analysis>", 1)[1]
            output_dict["analysis"] = analysis_content
        if "<alert-validation>" in raw_message and "</alert-validation>" in raw_message:
            validation_tag = raw_message.split("</alert-validation>", 1)[0].split("<alert-validation>", 1)[1]
            output_dict["alert-validation"] = validation_mapping.get(validation_tag.strip(), None)
        if "<attack-result>" in raw_message and "</attack-result>" in raw_message:
            attack_result_tag = raw_message.split("</attack-result>", 1)[0].split("<attack-result>", 1)[1]
            output_dict["attack-result"] = attack_result_mapping.get(attack_result_tag.strip(), None)
        if "<advice>" in raw_message and "</advice>" in raw_message:
            advice_parts = raw_message.split("</advice>")
            advice_content = advice_parts[0].split("<advice>", 1)[1]
            output_dict["advice"] = advice_content
        return json.dumps(output_dict).encode("urt-8")

    def iter_lines(
            self, chunk_size=ITER_CHUNK_SIZE, decode_unicode=False, delimiter=None
    ):
        accumulated_content = ""
        output_dict = {}
        analysis_flag = False
        validation_flag = False
        attack_result_flag = False
        advice_flag = False
        for chunk in self.completions:
            if not chunk.choices or not chunk.choices[0].delta.content:
                continue
            delta_content = chunk.choices[0].delta.content
            accumulated_content += delta_content
            #  下面解析成功的条件是返回结果是按照上面的顺序出来的
            if not analysis_flag and "<analysis>" in accumulated_content:
                if "</analysis>" in accumulated_content:
                    analysis_parts = accumulated_content.split("</analysis>")
                    analysis_content = analysis_parts[0].split("<analysis>")[1]
                    output_dict["analysis"] = analysis_content
                    analysis_flag = True
                else:
                    analysis_content = accumulated_content.split("<analysis>")[1]
                    output_dict["analysis"] = analysis_content
            if not validation_flag and "<alert-validation>" in accumulated_content and "</alert-validation>" in accumulated_content:
                validation_tag = accumulated_content.split("</alert-validation>")[0].split("<alert-validation>")[1]
                output_dict["alert-validation"] = validation_mapping.get(validation_tag.strip(), None)
                validation_flag = True
            if not attack_result_flag and "<attack-result>" in accumulated_content and "</attack-result>" in accumulated_content:
                attack_result_tag = accumulated_content.split("</attack-result>")[0].split("<attack-result>")[1]
                output_dict["attack-result"] = attack_result_mapping.get(attack_result_tag.strip(), None)
                attack_result_flag = True
            if not advice_flag and "<advice>" in accumulated_content:
                if "</advice>" in accumulated_content:
                    advice_parts = accumulated_content.split("</advice>")
                    advice_content = advice_parts[0].split("<advice>")[1]
                    output_dict["advice"] = advice_content
                    advice_flag = True
                else:
                    advice_content = accumulated_content.split("<advice>")[1]
                    output_dict["advice"] = advice_content
            if output_dict:
                # print(json.dumps(output_dict, ensure_ascii=False), flush=True)
                yield json.dumps(output_dict, ensure_ascii=False).encode(self.encoding)

class DeepSeekConnection:
    """负责网络 I/O 的连接类"""

    def __init__(self, host=None, api_secret=None, api_key=None, ):
        self.chat = AIModelChat(api_key=api_key, base_url=host, aimodel="deepseek-r1-250120")
        # super().__init__()
        # self.headers["Content-Type"] = "application/json"
        # self.is_connected = False
        # self.api_secret = api_secret
        # self.sign = None
        # self.host = host
        # self.api_key = api_key
        # self.authenticator = GPTAuthenticator(self)
        # self.url_prefix = "https://{}".format(
        #     self.host) if self.host is not None and "http" not in self.host else self.host

    # def prepare_request(self, request: Request) -> PreparedRequest:
    #     uri = request.url
    #     request.url = f"{self.url_prefix}{uri}"
    #     timestamp = int(time.time() * 1000)
    #     nonce = uuid.uuid4().hex
    #     # if request.method == "POST":
    #     if request.json is None:
    #         request.json = {}
    #     request.json.update({
    #         "timestamp": timestamp,
    #         "nonce": nonce
    #     })
    #
    #     # request.json.update({ "api_key": self.api_key, "api_secret": self.api_secret, "timestamp": timestamp, "nonce": nonce, })
    #     sign = self.get_sign(request.json)
    #     request.headers.update(
    #         {'timestamp': str(timestamp), 'nonce': nonce, 'sign': sign, "h": self.host, "p": self.url_prefix})
    #
    #     return super().prepare_request(request)
    #
    # def get_sign(self, json_data):
    #     json_str = json.dumps(json_data, sort_keys=True)
    #     self.sign = hmac.new(self.api_secret.encode('utf-8'), json_str.encode('utf-8'), 'sha256').hexdigest()
    #     return self.sign

    def request(self, method, url, **kwargs):
        from requests.models import Response
        stream = kwargs.pop("stream", False)
        body = kwargs.pop("json", None)
        r = Response()
        r.headers['Content-Type'] = 'application/json'
        if url == "/api/v2/openapi/workflow/list":
            workflow_list_msg = {
                "message": "success",
                "workflow_list": [
                    {
                        "id": "deepseek-client-id:Qaxgpt",
                        "parallel": 5,
                        "workflow_nodes": {
                            "agents": [
                                {"agent_name": "研判模型", "agent_id": "deepseek-agent"}
                            ]
                        },
                    }
                ]
            }
            r.status_code = 200
            r._content = json.dumps(workflow_list_msg).encode("utf-8")
            r.encoding = "utf-8"
            r.url = url
        elif url == "/api/v2/openapi/workflow/event_judge/run":
            if stream:
                return self.chat.alarm_judge_stream(body)
            else:
                return self.chat.alarm_judge(body)
        return r


class AIModelChat(object):
    """
    满足openai规范的其他AI模型使用-告警研判
    """

    def __init__(self, api_key=None, base_url=None, aimodel=None):
        self.api_key = api_key
        self.base_url = base_url
        self.aimodel = aimodel
        # self.init_config()
        self.client = OpenAI(
            api_key=api_key, base_url=base_url
        )

    #
    # def init_config(self):
    #     if not self.api_key and not self.base_url or not self.aimodel:
    #         with app.app_context():
    #             qgpt_config = SystemConfig.get_by_key(QGPT_CONFIG_KEY)
    #             qgpt_config = json.loads(qgpt_config.value) if qgpt_config else {}
    #             if not self.host:
    #                 self.host = qgpt_config.get('service')
    #             if not self.api_key:
    #                 self.api_key = qgpt_config.get('auth_key')
    #             if not self.api_secret:
    #                 self.api_secret = qgpt_config.get('auth_secret')
    #             if not self.host and not self.api_key or not self.api_secret:
    #                 raise "init_config error!"

    def get_alarm_prompt(self, alarm_data):
        return """
你是一名高级AI网络安全专家，负责分析安全告警。请使用专业网络安全术语，对告警进行全面而严谨的分析。你的分析需要遵循以下规则：
1. 清晰描述攻击者行为和意图以及最可能的下一步目标。
2. 结构清晰、步骤明确，并突出告警相关证据。
3. 全面考虑告警各个方面，尤其是告警内各实体（如攻击IP、受害IP、端口、URL、协议、请求参数、Payload数据）之间的技术关联。
4. 对可疑或异常元素进行技术细节解释。
5. 白名单与黑名单规则：
    - 白名单条件：如果告警行为符合正常业务程序调用（网络数据或者载荷里面涵盖的行为是正常的业务程序调用）则标记为“无效”（即非攻击）。
    - 黑名单条件：如果存在明确的威胁指标（如已知恶意IP、恶意Payload特征、已知的漏洞的POC或EXP等），则标记为“有效”（即为攻击）。
    - 若不满足白名单或黑名单条件，则标记为“暂不确定”。
    - 优先级：白名单条件优先于黑名单条件。
以下是你需要分析的安全告警的详细信息（JSON格式）：
<alert_data>%s</alert_data>
以下为告警信息对应的字段解释（JSON格式）：
<field_description>%s</field_description>
分析需分为以下四部分：
1. <analysis>:
    - 从网络安全视角系统审查<alert_data>及<field_description>，提取告警里的关键信息，明确各字段含义及潜在影响。
    - 解码payload（Base64编码）字段内容，并分析解码后的十六进制数据，识别OSI层1-4协议（例如TCP、UDP、ICMP）。记录解码内容。解析后对payload与相关数据进行技术分析尽可能解码还原更多信息。
    - 综合分析所有实体（攻击IP、受害IP、端口、URL、请求参数、Payload特征）之间的关联，识别可能的攻击向量及技术利用点。
    - 对告警中的异常与可疑元素（如混淆指令、特殊编码、已知恶意域名/IP）进行技术原理解释。
    - 考虑并列出对受害系统或网络的可能影响。如果有资产信息（asset_info）需要结合资产进行分析。
    - 考虑白名单与黑名单条件，并结合证据判断告警属于正常业务行为（白名单优先），或存在已知威胁指标（黑名单）。如果两者均不满足，则为暂不确定。如果存在已知威胁指标（黑名单），即代表本次告警为一次攻击，则需要给出详细的判断攻击结果的依据（比如，如果攻击成功，响应体会出现xx字样/受害机器会xx等等），以及最后的攻击结果（攻击成功、攻击失败、暂不确定）。”
    - 对告警性质进行判断（有效、无效、暂不确定），并列出关键支撑点与可能缓解策略
然后提供一份详细的分析总结，应包含：尽可能多的和分析相关的实体信息（如IP、URL、请求内容，响应内容，解码后的载荷，时间，命令参数等）。分析过程符合逻辑顺序，包括详细技术细节和原理说明，最终给出告警有效性（有效、无效、暂不确定）的结论及依据，如果有效请给出攻击者的意图、详细的攻击结果判断依据、攻击结果（攻击成功、攻击失败、暂不确定）以及可能进行的下一步计划。
**最后以约500字汇总以上信息，以叙述的方式输出内容。**仅提供最终的专业总结，不要附加额外内容。
2. <alert-validation>: 
若告警行为符合正常业务程序调用（符合白名单条件），则返回“无效”，若告警行为存在明确的威胁指标（符合黑名单条件）则返回“有效”，若不满足白名单或黑名单条件，则返回“暂不确定”。
3. <attack-result>: 
在先前条件的基础上，需对攻击结果进行状态判断，根据已知信息给出合理结论，返回以下之一：“攻击成功”、“暂不确定”、“攻击失败”。
4. <advice>: 在先前条件的基础上，需要给出几条处置建议。给出的处置建议需要遵循如下准则：
    - 格式：每个建议的格式为：1. **{处置建议小标题}**: {具体处置建议}，比如 “1. **告警加白**: 这是具体的处置建议”。
    - 内容：提供详细的建议，包括具体的操作步骤和技术细节，并且必须要使用<alert_data>中的相关实体（如攻击IP、受害IP、端口、URL、域名、账号等等），对于每个建议，确保描述清晰且逻辑连贯，便于执行。
    - 联动安全设备：如果需要与安全设备（如防火墙、WAF、IDS/IPS等）协同处理，请详细说明涉及的设备类型、所需执行的动作及参数或命令。
    - 考虑内部/外部IP通信：分析内部和外部IP之间的通信情况，特别要注意存在XFF（X-Forwarded-For）的情况。特别关注<alert_data>中提到的资产信息：asset_info，确保提出的处置建议不会对正常业务造成负面影响。
    - 业务影响评估：在提出每个建议时，务必考虑其对正常业务的影响，尽量减少干扰并确保业务连续性。如果某项措施可能带来显著影响，请明确指出并提供替代方案或缓解策略。
    - 特别注意：对于需要强化口令的，建议中需要包含账号、域名、端口、URL，以便进行更加详细的分析和考虑。
上面4个分析部分的结果请严格按照下面的格式返回：
<analysis>
[你的专业的分析总结]
</analysis>
<alert-validation>
[有效/无效/暂不确定]
</alert-validation>
<attack-result>
[攻击成功/攻击失败/暂不确定]
</attack-result>
<advice>
[根据需要提供详细的建议]
</advice>
""" % (json.dumps(alarm_data, ensure_ascii=False), json.dumps(field_desc, ensure_ascii=False))

    def alarm_judge(self, alarm_id=None, alarm_data=None, stream_flag=True):
        """
        告警研判，返回告警研判结果，包括总结、研判结论、研判结果和处置建议4个部分,格式是json
        :param alarm_id: 告警ID，在实际业务场景中可只传告警ID，告警数据在这里获取
        :param alarm_data: 具体告警数据，主要是为了调试
        :param stream_flag: 是否流式返回
        :return:
        """
        if not alarm_data and not alarm_id:
            raise "There is no data need to be judged!!!"
        if not alarm_data and alarm_id:
            # 根据alarm_id获取alarm_data
            # alarm_data, _ = CollectionAlarmInfoManage.make_qgpt_judgement_alarm_info(
            #     start_time, end_time, alarm_id
            # )
            pass
        # 获取提问模板
        content = self.get_alarm_prompt(alarm_data)
        if stream_flag:
            return self.alarm_judge_stream(content)
        else:
            return self.alarm_judge_no_stream(content)

    def alarm_judge_no_stream(self, content):
        response = self.client.chat.with_raw_response.completions.create(
            model=DOU_MODEL,  # your model endpoint ID
            messages=[
                {"role": "system", "content": "你是一名高级AI网络安全分析专家"},
                {"role": "user", "content": content},
            ],
        )
        completions = response.parse()
        return DeepSeekResponse(completions=completions, raw_response=response.http_response)
        # completion = self.client.chat.completions.create(
        #     model=DOU_MODEL,  # your model endpoint ID
        #     messages=[
        #         {"role": "system", "content": "你是一名高级AI网络安全分析专家"},
        #         {"role": "user", "content": content},
        #     ],
        # )
        # return self.parse_alarm_judge_result(completion.choices[0].message.content)

    # def parse_alarm_judge_result(self, result):
    #     """
    #     解析非流式输出的研判结果，格式为prompt中的格式
    #     :param result:
    #     :return:
    #     """
    #     output_dict = {}
    #     if not result:
    #         return output_dict
    #     if "<analysis>" in result and "</analysis>" in result:
    #         analysis_parts = result.split("</analysis>")
    #         analysis_content = analysis_parts[0].split("<analysis>", 1)[1]
    #         output_dict["analysis"] = analysis_content
    #     if "<alert-validation>" in result and "</alert-validation>" in result:
    #         validation_tag = result.split("</alert-validation>", 1)[0].split("<alert-validation>", 1)[1]
    #         output_dict["alert-validation"] = validation_mapping.get(validation_tag.strip(), None)
    #     if "<attack-result>" in result and "</attack-result>" in result:
    #         attack_result_tag = result.split("</attack-result>", 1)[0].split("<attack-result>", 1)[1]
    #         output_dict["attack-result"] = attack_result_mapping.get(attack_result_tag.strip(), None)
    #     if "<advice>" in result and "</advice>" in result:
    #         advice_parts = result.split("</advice>")
    #         advice_content = advice_parts[0].split("<advice>", 1)[1]
    #         output_dict["advice"] = advice_content
    #     return output_dict

    def alarm_judge_stream(self, content):
        completions = self.client.chat.completions.create(
            model=self.aimodel,  # your model endpoint ID
            messages=[
                {"role": "system", "content": "你是一名高级AI网络安全分析专家"},
                {"role": "user", "content": content},
            ],
            stream=True
        )
        return DeepSeekResponse(completions=completions, raw_response=completions.response)
        # accumulated_content = ""
        # output_dict = {}
        # analysis_flag = False
        # validation_flag = False
        # attack_result_flag = False
        # advice_flag = False
        # for chunk in stream:
        #     if not chunk.choices or not chunk.choices[0].delta.content:
        #         continue
        #     delta_content = chunk.choices[0].delta.content
        #     accumulated_content += delta_content
        #     #  下面解析成功的条件是返回结果是按照上面的顺序出来的
        #     if not analysis_flag and "<analysis>" in accumulated_content:
        #         if "</analysis>" in accumulated_content:
        #             analysis_parts = accumulated_content.split("</analysis>")
        #             analysis_content = analysis_parts[0].split("<analysis>")[1]
        #             output_dict["analysis"] = analysis_content
        #             analysis_flag = True
        #         else:
        #             analysis_content = accumulated_content.split("<analysis>")[1]
        #             output_dict["analysis"] = analysis_content
        #     if not validation_flag and "<alert-validation>" in accumulated_content and "</alert-validation>" in accumulated_content:
        #         validation_tag = accumulated_content.split("</alert-validation>")[0].split("<alert-validation>")[1]
        #         output_dict["alert-validation"] = validation_mapping.get(validation_tag.strip(), None)
        #         validation_flag = True
        #     if not attack_result_flag and "<attack-result>" in accumulated_content and "</attack-result>" in accumulated_content:
        #         attack_result_tag = accumulated_content.split("</attack-result>")[0].split("<attack-result>")[1]
        #         output_dict["attack-result"] = attack_result_mapping.get(attack_result_tag.strip(), None)
        #         attack_result_flag = True
        #     if not advice_flag and "<advice>" in accumulated_content:
        #         if "</advice>" in accumulated_content:
        #             advice_parts = accumulated_content.split("</advice>")
        #             advice_content = advice_parts[0].split("<advice>")[1]
        #             output_dict["advice"] = advice_content
        #             advice_flag = True
        #         else:
        #             advice_content = accumulated_content.split("<advice>")[1]
        #             output_dict["advice"] = advice_content
        #     if output_dict:
        #         # print(json.dumps(output_dict, ensure_ascii=False), flush=True)
        #         yield json.dumps(output_dict, ensure_ascii=False)


# class DeepSeek




if __name__ == '__main__':
    alarm_data = {
        "last_access_time": 1741173848000,
        "attacker": "10.95.54.207",
        "victim": "10.41.208.17",
        "level": 1,
        "sip": "10.95.54.207",
        "dip": "10.41.208.17",
        "sport": 40720,
        "dport": 8081,
        "host": "artifactory-direct",
        "rule_id": "0x10020d4d",
        "protocol": "http",
        "xff": "",
        "threat_name": "发现使用PUT方式上传可疑文件",

        "start_time": 1741104000000,
        "end_time": 1741190399000,
        "id": "20250305_2a23057c89e83799299e4eeb914a6c81",
        "sip_ioc_dip": "8ed277d109bd97785c83d442eabeb4f4",
        "skyeye_type": "webids-webattack_dolog",
        "type_chain": "16110000",

        "ioc": "",

        "branch_id": "QbJK/drix",
        "gpt_result": 3,
        "gpt_attack_result": 3,

        "uri": "/artifactory/qianxin-maven-snapshot-local/com/qax/ngsoc/sso-service/BD-2.3.0-SNAPSHOT/sso-service-BD-2.3.0-20250305.073959-9.jar",
        "req_param": "",
        "result": 0,
        "status_code": "201",
        "vuln_desc": "发现使用PUT方式上传可疑文件",
        "vuln_type": "文件上传",
        "payload": "",
        "req_header": "PUT /artifactory/codesafe-sastweb-snapshots-local/cn/com/codesec/skyconfig-languages/1.2.0-SNAPSHOT/skyconfig-languages-1.2.0-20250305.112408-2.jar HTTP/1.1\r\nUser-Agent: curl\r\nHost: artifactory-direct\r\nConnection: close\r\nContent-Length: 3070\r\nCache-control: no-cache\r\nPragma: no-cache\r\nAccept-Encoding: gzip,deflate\r\nAuthorization: Basic emhhbmdodWkxMDpBUDlIc1Jab3QzVXJGOXI2ajlyTHp6R3JhQ2Q=\r\n\r\n",
        "agent": "curl\r",
        "req_method": "PUT",
        "req_body": "PK\u0003\u0004\n\u0000\b\b\b\u0000\u0004eZÏç»z\u0007\u0000\u0000¾\u0015\u0000\u0000\u0014\u0000\u0000\u0000META-INF/MANIFEST.MFXÛrÛ6\u0010}÷ÿA?\u00007É²ßN§I¦i;M×\fDB\"(`\u0000PòõÝÅ¤$ÊÎ£°Ã½]è3mùiC¾1¥¹l\u0017I\u0014ßßý¦\u00185¬$ïOÏw\u001d-*¶øL\u000f¬]dÑ:JîïÞ÷\\\u0018+ýYÑvWõ<ÝiI>{@yâh\u0005@jMþ¡¦z^<èý©íïH)MË\fI¢4É¿ÞýóåÃß_£ª©R!\u0015\u000b*÷wK-7laÇ·jz ºP¼\u0003E@zUw'\u0005xô\u0006`w2\u0004¤ö-½ªû\u0005Ó\b ½£dÇáL¿\u0001\u0007HE7ÿMÚ\u001a¡rGI\u0012%#¢úÖð,ZF\u0013|ù\u0003\u0012èfQîN¤ÚEtÃv221AO²7ÏP\u001c®¡3Ç¨Ö\u0012ã«4ñ×\t_óáD\u001b1¯\u0002HÖñÒ¤~Úí-\u0015×Ò7pô×¾\u0004H¨dN\u001d\u000b%özÂõ­\u0000¤\u0013aí·<APg0fêÀÛrÕ\u000b\u0010b¿\"/µ\u0005h°Å\t:ÛÒÂ\u0010ìu@Z9a'Ø±×¤7\\h\u0010e¡\\'¶FI±\u0015ò4²dsð\u0004Ê/t·cÊ)iB\u001c\u001e'Î7\rÅøi\u0014Zï.äXV\u001ahª¡i'k\u0019¸c¨t¬Ì*\b­×$¶ÇôP)Îæ4ò®\u001e¨à%5@vÜ^£?Þy$YRbû\u0005­÷mU ½\u001dEOà }\u0006²ºåÛ(óN1Ý\u0003ß¾|¯2ý\fvðõ¯òÖÜ´·b\r\u001b4\u0000iÆdë×ê7ª\u0011¸ëÀK\b<ÚqBsÚ@ü´e¡ÕO^Ì\\\u0001¤±ú°±n\u0019QIzSF[*\u000b~y¯zb\u0015QkÞ\u0018o, a¨âÛY\u001dK~®L/2©lºz|à¦®\n|á\u0016{¼\u0005ªt+UCãÇ4Jò@»Ù\u0003O\u0019^w\u0018'\u000e\u0003m#%f »Á\u000b#?¯:íF2[ãNL{#]Ø{Å¦ÊÖÃ\u000eÆ=ÁÎ§n7ði8Eë\u0006ïhQ0­¥Ògâàù\u001eh\u0004D\u001fmx[Ú^Ìm/r@\u0002\u0015`+~\u0018\u001b\u0016b3´¦¦1µã,J\u0007ÚÚ\f\u0014o_'?´2 ùpV´ò×flðºo¹!ußq\fÞ\u0012Íæ\u0004øm\u0010¢w^\u000eS»Ååµãüé­NP\u0019õ=¼1à\u0002Ò®·Þ\u0006\u0016JæÍ\u0001Z£¾m(Ä®U\u0006\u0013üÔXÐÈbÏ'Ò\u001c·>\u001f7RCèè\u000eIÂ\u0005ðââ¹\u0011\u0013\u0004¬\u0006\u0016Ì\u001dÜ]ÛH©$/ÝiNã$Kx\u001d\u001d(-yÕ£­Ã\u0015rySÊ TìW­Ñ)8\u0013®À\u0017!P¢\u0007/m0ÑÍ8Z&ë§§s\r@\u001axÓkÍ-·7<:&\nìÖ\u0014«öiµôZ¨a·EÉ*\u000bIÑ*ÓùAu\u0013¦ùU^¾ÑÆ×ÇÖ¦Ö®Ë>nWn÷µoF\u0018uvÎ9\u001e\u000fÍ6\u0014¬\u0013r×é\u0014Ê\u0010-¶xÎq\"tÎP:\u0005}qê3{y\\÷\u0000q\u001a\u0005Þ\u0018*»3o©îXaê\u0017\u0006»²\tL¼][ªßN\u0001)ÖÃR;2°å¡)õ\u0006a\u000b&|*·éTé\u0013Ú\u001eï$«q\u000e\u0015¶a´uë\u0016\tHù¹\u001c\\ßqÿT9/M)\u00048ió.Å¸û\nnË,¹¼X²\u0002Ûyy\u0013\u0010\u001f\u0010\u0003ÞPã Ø\u0001eÚb_]ã\nÊºb\bâË\u000f\u001bä'ûKY\u0018dL«3.\u0011fu\t/7ÜzMn*È \u0016I\u001eJÙ@Ý`ñú¨ª\u0007îÁXzçk@²ï1O³àá\u000eó:õ\u0007H\u001bsí\tR+æ+\u000b¸róÎ­ ~Ø\u0018ÓA6Fs¤ÂüêØíY^\u0018n\"\u0001ºººêX;Ç\u0018\r[\u000e¼¦ÛjzdíÙlÀ`¦M\u0004ßàt&u¹\u000fÕÁ~6Ru{½Æ!ä Ýw®Âc\u001e\u0001àÃïÀ¥På$Ð S\u001cV $K\\\u0015ÒñÌàÛ?\u001e\u0007Z %ô\u001c{Y'ç¸Ù{\u0011;ÚÒÄôÍ\\4Ç¹ÓºÜ\u0014þ|ØU\u0014ªÈÚêý:2\u0005ÙüØ8ú\u001a\"hdSP·¬\u000bfü¸\u0001¤l@ò\u001a@ZAt~\u000e/ÄñÖ\bz\u0001%4w\u000f¹M\u0011ÿúº\u0010Þ\u0000ÄyçU¢B¤as\u0012{C\u0017´\n1âÔ-\u0003ãúèUo½:I2f^ÃÏ}=ÈMÍZ¦¹å§èvËp5ÁÐÔ\u0015+öàè\n|f!òL)©¾Ã{£eßmÓbß\r¼\u000ejUj7»4=\u001bÝíØ\u0011)\u0005,n,×\u0003Ï,\u0011µ«xÂ\u0006Àbâ÷ÖÑ4cO¹\n3XA7yaÃ[ rÇÆáìáÃþ7((¶\u0015\fyÜà`Yó)ÈxÑCÿ<\u000ek\u0015«\u001cØ¿îÒ'W+öiK¡2\u0017ø\u001e\u0001×Q\u0016\u0007åòp\"\f\b§Óøä3Ee7ñdEâ4>¹\u0007&Ð»áo\f?óÒdóÍÂnéù|²lô\u000fÿë=6\u0018\u001a9D\u0012J§¨$©L©Ïýùý\u001dv¡}±:þÊ`Ï¿p\u0000ô°­ê+Õo¬-á\u0011ö±|^\u0014m\u0004p\njV\\iþ÷ïÏ\u000b$Rýüà\"âò\u0001ê­á¨§ë\u000f¾\u0019]\b\u001e`ß²®®¨b%\n8-üL|ø5\u0003f§ÿ\u001aÝßÝßý\u000fPK\u0007\bÏç»z\u0007\u0000\u0000¾\u0015\u0000\u0000PK\u0003\u0004\n\u0000\u0000\b\u0000\u0000\u0004eZ\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\t\u0000\u0000\u0000META-INF/PK\u0003\u0004\n\u0000\u0000\b\u0000\u0000\u0004eZ\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0003\u0000\u0000\u0000cn/PK\u0003\u0004\n\u0000\u0000\b\u0000\u0000\u0004eZ\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0007\u0000\u0000\u0000cn/com/PK\u0003\u0004\n\u0000\u0000\b\u0000\u0000\u0004eZ\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u000f\u0000\u0000\u0000cn/com/codesec/PK\u0003\u0004\n\u0000\u0000\b\u0000\u0000\u0004eZ\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0014\u0000\u0000\u0000cn/com/codesec/text/PK\u0003\u0004\n\u0000\u0000\b\u0000\u0000\u0004eZ\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u001d\u0000\u0000\u0000cn/com/codesec/text/language/PK\u0003\u0004\n\u0000\b\b\b\u0000\u0004eZ|@\u0001G¸\u0000\u0000\u0000í\u0000\u0000\u00004\u0000\u0000\u0000cn/com/codesec/text/language/LanguageExtractor.classeM±\u000e@\f}\u0007\b\u001aÜ\u001cÜÔ[\u001cÑè q?ÎÆ`\u0004\u0012<\f¿ådâà\u0007øQÆBÜlÓ×¾¶yïýy¾\u0000ÌÐõ`\t\u0004::K¸t%-\rF^Tz*Ôdø\u001bV¥É6YîÁ\u0011èÕMÕOr\u001bI\u001b\u0001w\u001e§±Y\bØãÉAÀY²\u000f\u001b­\u000e\u001ap\u0005zaÒ¦H\"Ê÷*º¿Ë\\Ó:®ÈàÏ(¨<0\u0002+¢\nÁÉJ\u001e³aÍÆôæ½>ûn½l2¶¹[è|\u0001PK\u0007\b|@\u0001G¸\u0000\u0000\u0000í\u0000\u0000\u0000PK\u0001\u0002\u0014\u0003\u0014\u0000\b\b\b\u0000\u0004eZÏç»z\u0007\u0000\u0000¾\u0015\u0000\u0000\u0014\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000¤\u0000\u0000\u0000\u0000META-INF/MANIFEST.MFPK\u0001\u0002\u0014\u0003\n\u0000\u0000\b\u0000\u0000\u0004eZ\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\t\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0010\u0000íA¼\u0007\u0000\u0000META-INF/PK\u0001\u0002\u0014\u0003\n\u0000\u0000\b\u0000\u0000\u0004eZ\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0003\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0010\u0000íAã\u0007\u0000\u0000cn/PK\u0001\u0002\u0014\u0003\n\u0000\u0000\b\u0000\u0000\u0004eZ\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0007\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0010\u0000íA\u0004\b\u0000\u0000cn/com/PK\u0001\u0002\u0014\u0003\n\u0000\u0000\b\u0000\u0000\u0004eZ\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u000f\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0010\u0000íA)\b\u0000\u0000cn/com/codesec/PK\u0001\u0002\u0014\u0003\n\u0000\u0000\b\u0000\u0000\u0004eZ\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0014\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0010\u0000íAV\b\u0000\u0000cn/com/codesec/text/PK\u0001\u0002\u0014\u0003\n\u0000\u0000\b\u0000\u0000\u0004eZ\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u001d\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0010\u0000íA\b\u0000\u0000cn/com/codesec/text/language/PK\u0001\u0002\u0014\u0003\u0014\u0000\b\b\b\u0000\u0004eZ|@\u0001G¸\u0000\u0000\u0000í\u0000\u0000\u00004\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000¤Ã\b\u0000\u0000cn/com/codesec/text/language/LanguageExtractor.classPK\u0005\u0006\u0000\u0000\u0000\u0000\b\u0000\b\u0000\u000b\u0002\u0000\u0000Ý\t\u0000\u0000\u0000\u0000",
        "rsp_header": "HTTP/1.1 201 Created\r\nX-JFrog-Version: Artifactory/7.59.16 75916900\r\nX-Artifactory-Id: 4b6603b64eb96691600e06286d6e10222c175793\r\nX-Artifactory-Node-Id: art2\r\nLocation: https://af-biz.qianxin-inc.cn/artifactory/codesafe-sastweb-snapshots-local/cn/com/codesec/skyconfig-languages/1.2.0-SNAPSHOT/skyconfig-languages-1.2.0-20250305.112408-2.jar\r\nX-Checksum-Sha256: 02be9078af94d504ae4ef4e87e96342c436372727b2901d7488a4a708c199e1c\r\nContent-Type: application/vnd.org.jfrog.artifactory.storage.ItemCreated+json;charset=ISO-8859-1\r\nTransfer-Encoding: chunked\r\nDate: Wed, 05 Mar 2025 11:24:08 GMT\r\nConnection: close\r\n\r\n",
        "rsp_body": "{\n  \"repo\" : \"codesafe-sastweb-snapshots-local\",\n  \"path\" : \"/cn/com/codesec/skyconfig-languages/1.2.0-SNAPSHOT/skyconfig-languages-1.2.0-20250305.112408-2.jar\",\n  \"created\" : \"2025-03-05T19:24:09.103+08:00\",\n  \"createdBy\" : \"zhanghui10\",\n  \"downloadUri\" : \"https://af-biz.qianxin-inc.cn/artifactory/codesafe-sastweb-snapshots-local/cn/com/codesec/skyconfig-languages/1.2.0-SNAPSHOT/skyconfig-languages-1.2.0-20250305.112408-2.jar\",\n  \"mimeType\" : \"application/java-archive\",\n  \"size\" : \"3070\",\n  \"checksums\" : {\n    \"sha1\" : \"ad6d2c7fd3ec41dcd43959eea0baf3bc4aa695fc\",\n    \"md5\" : \"520f8f6962e02ca232ee269a1bdf158b\",\n    \"sha256\" : \"02be9078af94d504ae4ef4e87e96342c436372727b2901d7488a4a708c199e1c\"\n  },\n  \"originalChecksums\" : {\n    \"sha256\" : \"02be9078af94d504ae4ef4e87e96342c436372727b2901d7488a4a708c199e1c\"\n  },\n  \"uri\" : \"https://af-biz.qianxin-inc.cn/artifactory/codesafe-sastweb-snapshots-local/cn/com/codesec/skyconfig-languages/1.2.0-SNAPSHOT/skyconfig-languages-1.2.0-20250305.112408-2.jar\"\n}"
    }
    connection = DeepSeekConnection(api_key=DOU_TOKEN, host=DOU_URL)

    chat_instance = AIModelChat(api_key=DOU_TOKEN, base_url=DOU_URL, aimodel=DOU_MODEL)
    res = chat_instance.alarm_judge(alarm_data=alarm_data, stream_flag=False)
    print(res)

    # for res in chat_instance.alarm_judge(alarm_data=alarm_data, stream_flag=True):
    #     print(res)

    # print(chat_instance.alarm_judge(alarm_data=alarm_data, stream_flag=False))

    # {"analysis": "\n该告警涉及攻击者IP 10.95.54.207通过HTTP PUT方法向目标主机artifactory-direct（10.41.208.17:8081）上传JAR文件至Maven快照仓库。关键证据显示请求头包含Base64编码的凭证（用户zhanghui10），响应状态码201及Artifactory返回的完整资源路径表明文件成功写入。二进制载荷头部包含PK标识符，符合ZIP/JAR文件结构，META-INF目录存在标准清单文件，但未检测到已知恶意代码特征（如webshell或漏洞利用链）。异常点包括使用curl工具执行敏感操作、快照版本号（20250305.112408-2）异常接近当前时间戳，以及内部IP间未经过反向代理（XFF字段为空）。攻击意图可能为供应链攻击植入后门组件，后续可能通过依赖调用触发恶意行为。由于缺乏明确的IOC匹配且业务系统存在合法构件上传场景，暂无法排除自动化构建流程可能性。\n\n根据白名单规则，若zhanghui10账号具备该仓库写权限且文件内容经审核，则属于正常业务操作；反之若账号异常或文件含隐蔽恶意功能，则符合黑名单条件。当前证据链不完整，需结合代码审计及用户行为分析进一步判定。\n", "alert-validation": 4, "attack-result": 1, "advice": "\n1. **凭证有效性验证**：立即核查账号zhanghui10在artifactory-direct（10.41.208.17:8081）的权限范围，通过JFrog API调用`/api/security/users/zhanghui10`确认其仓库写权限是否超出业务需求。若存在过度权限，需按最小权限原则调整ACL策略。\n\n2. **文件深度检测**：使用沙箱对/cn/com/codesec/skyconfig-languages/1.2.0-SNAPSHOT/skyconfig-languages-1.2.0-20250305.112408-2.jar（SHA256:02be9078af94d504ae4ef4e87e96342c436372727b2901d7488a4a708c199e1c）进行静态特征扫描和动态行为分析，重点检查LanguageExtractor.class的反射调用、外部连接等异常操作码。\n\n3. **网络层拦截**：在边界防火墙（如Palo Alto PA-5200系列）临时添加策略，阻断10.95.54.207到10.41.208.17:8081的PUT方法，规则示例：`set security policies from-zone untrust to-zone trust policy ALERT_20250305 match source-address 10.95.54.207 destination-address 10.41.208.17 application junos-http then deny`，同时开启日志记录用于溯源。\n\n4. **双因素认证增强**：对Artifactory账号zhanghui10启用TOTP认证，通过REST API更新用户属性：`PUT /api/security/users/zhanghui10` 请求体追加`\"totp\": true`，并限制该账号仅允许从CI/CD服务器IP（非当前攻击IP）访问。\n\n5. **进程链审计**：在受害主机10.41.208.17上使用sysmon检查与8081端口关联的java进程树，执行命令`sysmon -query \"ProcessCreate where CommandLine contains '8081'\"`，验证Artifactory服务启动路径是否被篡改。\n"}
