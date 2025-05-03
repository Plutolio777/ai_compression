from typing import Optional, Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import logging

from compression_selector.tools import register

logger = logging.getLogger(__name__)


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
            <plans plans_id={方案1的id}>
            <plan index={文件的index}>
            <file_name>
            {文件名称}
            </file_name>
            <compression>
            {压缩算法}
            </compression>
            </plan>
            <plan index={文件的index}>
            <file_name>
            {文件名称}
            </file_name>
            <compression>
            {压缩算法}
            </compression>
            </plan>
            </plans>

            <plans plans_id={方案2的id}>
            <plan index={文件的index}>
            <file_name>
            {文件名称}
            </file_name>
            <compression>
            {压缩算法}
            </compression>
            </plan>
            <plan index={文件的index}>
            <file_name>
            {文件名称}
            </file_name>
            <compression>
            {压缩算法}
            </compression>
            </plan>
            </plans>
            
            注：压缩算法智能从该列表中进行选择，返回方案时也使用同样的名称 %s
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
        """初始化模型实例"""
        try:
            if self.model_config['model_type'].startswith('deepseek'):
                return ChatOpenAI(
                    model=self.model_config['sub_model'],
                    api_key=self.model_config['api_key'],
                    base_url=self.model_config['base_url'],
                    temperature=self.model_config['temperature'],
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
        return self.llm.invoke(prompt.format_messages())


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
    response = invoker.decision_intelligence(files)
    print(response.content)