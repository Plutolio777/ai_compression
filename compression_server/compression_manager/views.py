from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import StreamingHttpResponse, JsonResponse
from .serializers import FileUploadSerializer
from .models import CompressionTask, TempUploadedFile
from model_invoker import ModelInvoker
from file_manager.models import File
from lxml import etree
import uuid
import json
from django.contrib.auth.decorators import login_required
class FileUploadView(APIView):
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = serializer.save()
            return Response({
                'success': True,
                'file_id': str(uploaded_file.id),
                'task_id': str(uploaded_file.task.id)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def analysis_view(request):

        print(111111111111111)
        # 强制设置Accept头为text/event-stream
        request.accepted_renderer = None
        request.accepted_media_type = 'text/event-stream'
        
        task_id = request.GET.get('task_id')
        if not task_id:
            return JsonResponse({'error': 'task_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        user_id = request.GET.get('user_id')
        if not task_id:
            return JsonResponse({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        # 1. 查询关联的临时文件
        files = TempUploadedFile.objects.filter(task_id=task_id)
        if not files.exists():
            return JsonResponse({'error': 'No files found for this task'}, status=status.HTTP_404_NOT_FOUND)
        print(files)
        print(request.user.__dict__)
        print(request.user.id)
        # 2. 获取用户模型配置
        from model_manager.models import ModelConfig
        try:
            model_config = ModelConfig.objects.get(
                user=user_id,
                model_type='deepseek'
            )
            config = {
                "model_type": model_config.model_type,
                "sub_model": model_config.sub_model,
                "api_key": model_config.api_key,
                "base_url": model_config.endpoint,
                "temperature": str(model_config.temperature),
            }
        except ModelConfig.DoesNotExist:
            config = None
        print(config)
        # 3. 准备模型输入
        file_data = [{
            'index': idx,
            'name': file.original_name,
            'size': file.size,
            'type': file.type or file.original_name.split('.')[-1].upper()
        } for idx, file in enumerate(files)]

        # 4. 创建流式响应
        def generate():
            invoker = ModelInvoker(config)
            ai_res = invoker.decision_intelligence(file_data)
            buffer = ""
            think_over = False
            think_start = 0
            think_end = -1
            think = ""
            aiPlanList = []
            title_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
            title_index = 0
            
            for res_item in ai_res:

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
                    "files": plan_list,
                    "exception": root.xpath('//except/text()')[0].strip(),
                }

                for plan in root.xpath('//plan'):
                    plan_list.append({
                        "id": plan.get('index'),
                        "size": "100MB",
                        "name": plan.xpath('./file_name/text()')[0].strip(),
                        "selectedAlgorithm": plan.xpath('./compression/text()')[0].strip(),
                        "showAlgorithmList": False
                    })
                res_dict["think"] = think
                res_dict["think_over"] = True
                aiPlanList.append(plan_info)
                res_dict["aiResults"] = aiPlanList
                yield f'data: {json.dumps(res_dict)}\n\n'
                title_index += 1
                buffer = buffer[plans_end + 8:]

            res_dict = {
                "think": think,
                "aiResults":aiPlanList,
                "think_over": True,
                "aiResultsOver": True
            }
            yield f'data: {json.dumps(res_dict)}\n\n'
            
        response = StreamingHttpResponse(
            generate(), 
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
            }
        )
        return response



class TaskStatusView(APIView):
    def get(self, request, task_id):
        try:
            task = CompressionTask.objects.get(id=uuid.UUID(task_id))
            return Response({
                'success': True,
                'status': task.status,
                'analysis_result': task.analysis_result
            })
        except CompressionTask.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Task not found'
            }, status=status.HTTP_404_NOT_FOUND)
