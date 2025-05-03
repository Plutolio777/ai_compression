from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import ModelConfig, ModelCallRecord
from .serializers import ModelConfigSerializer, ModelCallRecordSerializer
from .utils import ModelInvoker
import requests
from django.utils import timezone
from asgiref.sync import sync_to_async


class ModelConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        configs = ModelConfig.objects.filter(user=request.user)
        serializer = ModelConfigSerializer(configs, many=True)
        
        # 构建前端需要的格式
        data = {
            'deepseek': {'apiKey': '', 'endpoint': '', 'temperature': 0.7, 'maxTokens': 2048, 'subModel': ''},
            'openai': {'apiKey': '', 'endpoint': 'https://api.openai.com/v1', 'temperature': 0.7, 'maxTokens': 2048, 'subModel': ''},
            'anthropic': {'apiKey': '', 'endpoint': 'https://api.anthropic.com/v1', 'temperature': 0.7, 'maxTokens': 2048, 'subModel': ''}
        }
        
        for config in serializer.data:
            import logging
            print(config)
            model_type = config['model_type']
            data[model_type] = {
                'apiKey': config['api_key'],
                'endpoint': config['endpoint'],
                'temperature': config['temperature'],
                'maxTokens': config['max_tokens'],
                'isConnected': config['is_connected'],
                'subModel': config.get('sub_model', '')
            }
        
        return Response({'success': True, 'data': data})

    def post(self, request):
        model_type = request.data.get('model_type')
        if model_type not in dict(ModelConfig.MODEL_TYPES).keys():
            return Response({'success': False, 'error': '无效的模型类型'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        data = {
            'model_type': model_type,
            'api_key': request.data.get('apiKey', ''),
            'endpoint': request.data.get('endpoint', ''),
            'temperature': request.data.get('temperature', 0.7),
            'max_tokens': request.data.get('maxTokens', 6048),
            'sub_model': request.data.get('subModel', '')
        }
        print(data)
        serializer = ModelConfigSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True})
        return Response({'success': False, 'error': serializer.errors}, 
                      status=status.HTTP_400_BAD_REQUEST)

class TestConnectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        model_type = request.data.get('model_type')
        config = ModelConfig.objects.filter(
            user=request.user, 
            model_type=model_type
        ).first()
        
        if not config:
            return Response({'success': False, 'error': '请先配置模型'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 模拟API测试
            is_connected = True
            response_time = 328  # 模拟响应时间
            
            # 更新连接状态
            config.is_connected = is_connected
            config.save()
            
            # 创建调用记录
            ModelCallRecord.objects.create(
                config=config,
                response_time=response_time,
                success=True
            )
            
            return Response({
                'success': True,
                'is_connected': is_connected,
                'response_time': response_time
            })
        except Exception as e:
            # 创建失败记录
            ModelCallRecord.objects.create(
                config=config,
                response_time=0,
                success=False,
                error_message=str(e)
            )
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class CallRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        model_type = request.query_params.get('model_type')
        config = ModelConfig.objects.filter(
            user=request.user,
            model_type=model_type
        ).first()
        
        if not config:
            return Response({'success': False, 'error': '请先配置模型'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        records = ModelCallRecord.objects.filter(config=config).order_by('-called_at')[:100]
        serializer = ModelCallRecordSerializer(records, many=True)
        return Response({'success': True, 'data': serializer.data})

class ModelTestView(APIView):
    permission_classes = [IsAuthenticated]

    async def post(self, request):
        """测试模型调用接口"""
        prompt = request.data.get('prompt')
        if not prompt:
            return Response({'success': False, 'error': '请输入prompt'},
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            invoker = ModelInvoker.get_instance()
            response = await invoker.invoke(
                prompt=prompt,
                system_message="你是一个有帮助的AI助手"
            )
            
            # 记录调用
            ModelCallRecord.objects.create(
                config=ModelConfig.objects.filter(
                    user=request.user,
                    model_type='deepseek'
                ).first(),
                response_time=0,  # 实际使用时应该计算
                success=True,
                prompt=prompt[:500],  # 截断避免过长
                response=response[:1000]
            )
            
            return Response({
                'success': True,
                'response': response
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
