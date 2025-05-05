from threading import Thread
from typing import Optional, Dict, Any
import json
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import logging
from queue import Queue
from compression_selector.tools import register
from lxml import etree
logger = logging.getLogger(__name__)


class StreamCallback(StreamingStdOutCallbackHandler):
    """自定义流式回调处理器"""

    def __init__(self):
        super().__init__()
        self.token_queue = Queue()

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.token_queue.put(token)

    def on_llm_end(self, response, **kwargs) -> None:
        self.token_queue.put(None)  # 结束信号


class ModelInvoker:
    """
    通用大模型调用工具类
    支持DeepSeek及其他可扩展模型
    """

    def __init__(self, model_config: Optional[Dict[str, Any]] = None):
        """
        初始化模型调用器

        Args:
            model_config: 模型配置字典，包含:
                - sub_model: 模型名称 (如 'deepseek-chat')
                - api_key: API密钥
                - base_url: API基础URL
                - temperature: 温度参数
                - max_tokens: 最大token数
        """
        self.model_config = model_config
        self.system_prompt = """你是一个文件压缩专家，请根据以下文件信息：
            - 文件index 
            - 文件名
            - 文件大小
            - 文件类型
            - 文件上次访问时间 （可以缺省）
            - 文件标签 （可以缺省）
            
            
            为每个文件推荐最合适的压缩方案(至少生成一种方案)，并给出理由。输出格式如下：
            <think>
            {所有文件整体方案的选择理由}
            </think>

            <plans plans_id='{方案1的数字id}'>

            <except>
            {简短的期望 预计可节省空间 预计压缩时间等}
            </except>

            <plan index='{文件的index}'>
            <file_name>
            {文件名称}
            </file_name>
            <compression>
            {压缩算法}
            </compression>
            </plan>
            <plan index='{文件的index}'>
            <file_name>
            {文件名称}
            </file_name>
            <compression>
            {压缩算法}
            </compression>
            </plan>

            </plans>

            <plans plans_id='{方案2的数字id}'>
            <except>
            {简短的期望 预计可节省空间 预计压缩时间等}
            </except>
            <plan index='{文件的index}'>

            <file_name>
            {文件名称}
            </file_name>
            <compression>
            {压缩算法}
            </compression>
            </plan>
            <plan index='{文件的index}'>
            <file_name>
            {文件名称}
            </file_name>
            <compression>
            {压缩算法}
            </compression>
            </plan>
            </plans>
            
            决策过程中请严格遵守以下约定：
            1.压缩算法只能从该列表中进行选择，返回方案时也使用同样的名称 %s
            2.生成的内容生动有趣 可以使用vue能够识别的小图标
            3.可以针对同一批文件给出多种不同的方案（plans）plans中的plan是针对每个文件的压缩方案 不要在同一个plans中针对统一文件提供不同的plan
            4.<compression></compression>中的压缩算法内容 请严格按照我提供的压缩算法列表的文本值为主
            5.统一个<plans></plans>中不要出现 <file_name></file_name>相同的 <plan></plan>
            6.<think></think> 固定使用markdown语法，方案选择的理由需要全面，专业，文本结构合理，思路清晰，可以使用icon进行点缀 需要包含的固定内容 a.文件分析报告 b.方案选择理由 c.预期结果
        """ % register.compression_list()
        self.llm = self._init_model()

    @staticmethod
    def generate_files_prompt(files):
        file_descriptions = "\n".join(
            f"- 文件名: {file['name']}, 类型: {file['type']}, 大小: {file['size']}"
            for file in files
        )
        return f"请分析以下文件：\n{file_descriptions}"

    def _init_model(self) -> ChatOpenAI:
        """初始化模型实例（添加流式支持）"""
        try:
            if self.model_config['model_type'].startswith('deepseek'):
                return ChatOpenAI(
                    model=self.model_config['sub_model'],
                    api_key=self.model_config['api_key'],
                    base_url=self.model_config['base_url'],
                    temperature=self.model_config['temperature'],
                    streaming=True  # 启用流式模式
                )
            # 可扩展其他模型支持
            raise ValueError(f"Unsupported model: {self.model_config['model_name']}")
        except Exception as e:
            logger.error(f"Model initialization failed: {str(e)}")
            raise



    def decision_intelligence(self, files):
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=self.generate_files_prompt(files)),
        ])
        # 初始化回调
        callback = StreamCallback()
        self.llm.callbacks = [callback]

        # 在后台线程中执行模型调用
        message = prompt.format_messages()
        print(message)
        def generate():
            self.llm.invoke(message)

        Thread(target=generate).start()

        # 流式返回 tokens
        while True:
            token = callback.token_queue.get()
            if token is None:  # 结束信号
                break
            yield token


    @classmethod
    def get_instance(cls, model_config: Optional[Dict[str, Any]] = None):
        """获取模型调用器实例 (单例模式)"""
        if not hasattr(cls, '_instance'):
            cls._instance = cls(model_config)
        return cls._instance

if __name__ == '__main__':
    config = {
        "model_type": "deepseek",
        "sub_model": "deepseek-chat",
        "api_key": "sk-679b247ed1bb4e07916a3cac8363a601",
        "base_url": "https://api.deepseek.com",
        "temperature": "0.0",
    }
    files = [
        {"index":0, "name": "data.json", "size": "10MB", "type": "JSON"},
        {"index":1, "name": "image.png", "size": "50MB", "type": "PNG"},
        {"index":2, "name": "log.txt", "size": "2MB", "type": "Text"},
        {"index":3, "name": "archive.zip", "size": "200MB", "type": "ZIP"},
    ]

    invoker = ModelInvoker(model_config=config)
    res = invoker.decision_intelligence(files)


    def generate(response):
        buffer = ""
        think_over = False
        think_start = 0
        think_end = -1
        think = ""
        aiPlanList = []
        title_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        title_index = 0
        for res_item in response:

            res_dict = {}
            buffer += res_item

            if not think_over:
                # 等待起始标签
                if '<think>' not in buffer:
                    continue
                if think_start == 0:
                    think_start = 7
                if think_end == -1 and '</think>' in buffer:
                    think_end = buffer.index('</think>')
                res_dict["think"] = think or buffer[think_start:think_end]
                yield f'data: {json.dumps(res_dict)}\n\n'
                if think_end != -1:
                    think_over = True
                    think = buffer[think_start:think_end]
                    buffer = buffer[think_end + 9:]

                    res_dict["think"] = think
                    res_dict["think_over"] = True
                    yield f'data: {json.dumps(res_dict)}\n\n'

            if not think_over or '</plans>' not in buffer:
                continue
            res_dict["think"] = think
            plans_start = 0
            plans_end = buffer.index('</plans>')

            plans = buffer[plans_start:plans_end + 8]
            print(plans)
            root = etree.fromstring(plans.encode())
            plan_list = []
            plan_info = {
                "plan_id": root.get('plans_id'),
                "title": f"推荐方案 {title_list[title_index]}",
                "flies": plan_list,
                "exception": root.xpath('//except/text()')[0].strip(),
            }

            for plan in root.xpath('//plan'):
                plan_list.append({
                    "id": plan.get('index'),
                    "size": "100MB",
                    "name": plan.xpath('./file_name/text()')[0].strip(),
                    "selectedAlgorithm": plan.xpath('./compression/text()')[0].strip()
                })
            res_dict["think"] = think
            res_dict["think_over"] = True
            aiPlanList.append(plan_info)
            res_dict["aiResults"] = aiPlanList
            yield f'data: {json.dumps(res_dict)}\n\n'
            title_index += 1
            buffer = buffer[plans_end + 8:]

    for line in generate(res):
        print(line)



