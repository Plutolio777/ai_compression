from typing import Optional, Dict, Any
from langchain.llms.base import BaseLLM
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from django.conf import settings
import logging

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
                - model_name: 模型名称 (如 'deepseek-chat')
                - api_key: API密钥
                - base_url: API基础URL
                - temperature: 温度参数
                - max_tokens: 最大token数
        """
        self.model_config = model_config
        self.llm = self._init_model()
        
    def _init_model(self) -> BaseLLM:
        """初始化模型实例"""
        try:
            if self.model_config['model_name'].startswith('deepseek'):
                return ChatOpenAI(
                    model=self.model_config['sub_model'],
                    openai_api_key=self.model_config['api_key'],
                    openai_api_base=self.model_config['base_url'],
                    temperature=self.model_config['temperature'],
                    max_tokens=self.model_config['max_tokens']
                )
            # 可扩展其他模型支持
            raise ValueError(f"Unsupported model: {self.model_config['model_name']}")
        except Exception as e:
            logger.error(f"Model initialization failed: {str(e)}")
            raise
    
    async def invoke(self, prompt: str, system_message: Optional[str] = None) -> str:
        """
        调用模型生成回复
        
        Args:
            prompt: 用户输入提示
            system_message: 系统角色设定
            
        Returns:
            模型生成的回复内容
        """
        try:
            messages = []
            if system_message:
                messages.append(SystemMessage(content=system_message))
            messages.append(HumanMessage(content=prompt))
            
            response = await self.llm.agenerate([messages])
            return response.generations[0][0].text
        except Exception as e:
            logger.error(f"Model invocation failed: {str(e)}")
            raise
    
    def test():
        print("测试")
        pass

    @classmethod
    def get_instance(cls, model_config: Optional[Dict[str, Any]] = None):
        """获取模型调用器实例 (单例模式)"""
        if not hasattr(cls, '_instance'):
            cls._instance = cls(model_config)
        return cls._instance

# 示例用法:
# invoker = ModelInvoker.get_instance()
# response = await invoker.invoke("你好", "你是一个有帮助的AI助手")
