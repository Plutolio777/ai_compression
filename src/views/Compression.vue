<template>
  <!-- 上传区域 -->
  <div class="bg-white rounded-lg shadow-sm p-8 mb-6">
    <div
      class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition-colors"
      @dragover.prevent @drop.prevent="handleDrop" @click="triggerFileInput">
      <input type="file" ref="fileInput" class="hidden" multiple @change="handleFileChange" />
      <i class="fas fa-cloud-upload-alt text-5xl text-gray-400 mb-4"></i>
      <p class="text-gray-600">拖拽文件到此处或点击上传</p>
      <p class="text-gray-400 text-sm mt-2">支持 ZIP、RAR、7Z 等压缩文件格式</p>
    </div>
  </div>
  <!-- 文件列表 -->
  <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-lg font-medium">文件列表</h2>
      <div class="flex space-x-2">
        <button class="px-4 py-2 bg-blue-500 text-white !rounded-button whitespace-nowrap hover:bg-blue-600"
          @click="generateCompressionPlan">
          一键生成压缩方案
        </button>
        <button class="px-4 py-2 border border-gray-300 !rounded-button whitespace-nowrap hover:bg-gray-50"
          @click="clearFileList">
          清空列表
        </button>
      </div>
    </div>
    <div class="space-y-4">
      <div v-for="file in fileList" :key="file.id" class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
        <div class="flex items-center space-x-3">
          <i class="fas fa-file-archive text-blue-500 text-xl"></i>
          <div>
            <p class="font-medium">{{ file.name }}</p>
            <p class="text-sm text-gray-500">{{ file.size }}</p>
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <template v-if="file.status === 'pending'">
            <div class="flex items-center text-gray-400">
              <i class="fas fa-clock mr-2"></i>
              <span class="text-sm">未上传</span>
            </div>
          </template>
          <template v-else-if="file.status === 'uploading'">
            <div class="w-32">
              <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div class="h-full bg-blue-500 transition-all duration-300" :style="{ width: `${file.progress}%` }">
                </div>
              </div>
            </div>
            <span class="text-sm text-gray-600">{{ file.progress }}%</span>
          </template>
          <template v-else-if="file.status === 'success'">
            <div class="flex items-center text-green-500">
              <i class="fas fa-check-circle mr-2"></i>
              <span class="text-sm">上传成功</span>
            </div>
          </template>
          <button class="text-red-500 hover:text-red-600" @click="removeFile(file.id)">
            <i class="fas fa-trash-alt"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
  <!-- AI 分析结果 -->
  <div  class="bg-white rounded-lg shadow-sm p-6">
    <h2 class="text-lg font-medium mb-4">AI 分析建议</h2>
    <div class="space-y-4">

      <!-- 思考状态 -->
      <div v-if="thinkShow" class="p-4 bg-gray-50 rounded-lg flex justify-between items-center">
        <span class="text-gray-600">正在思考</span>
        <i v-if="isThinking" class="fas fa-circle-notch text-blue-500 fa-spin"></i>
        <i v-else class="fas fa-check-circle text-green-500"></i>
      </div>

      <!-- 实时输出 -->
      <div class="p-6 bg-blue-50 rounded-lg border border-blue-100">
        <pre class="text-gray-700 font-mono text-sm leading-relaxed whitespace-pre-wrap">{{ streamText }}</pre>
        <div v-if="isStreaming" class="mt-3 flex items-center text-blue-500">
          <i v-if="isAnalyzing" class="fas fa-circle-notch mr-2 fa-spin"></i>
          <i v-else class="fas fa-check-circle mr-2 text-green-500"></i>
          <span class="text-sm">正在分析...</span>
        </div>
      </div>

      <!-- 生成状态 -->
      <div v-if="generatShow" class="p-4 bg-gray-50 rounded-lg flex justify-between items-center">
        <span class="text-gray-600">正在生成压缩方案</span>
        <i v-if="isGenerating" class="fas fa-circle-notch text-blue-500 fa-spin"></i>
        <i v-else class="fas fa-check-circle text-green-500"></i>
      </div>

      <!-- 压缩方案列表 -->
      <div v-for="(result, index) in aiResults" :key="index" class="p-4 bg-blue-50 rounded-lg">
        <div class="flex items-center justify-between gap-4">
          <!-- 压缩方案名称 -->
          <h3 class="font-medium text-blue-700">{{ result.title }}</h3>
          <!-- 压缩方案操作列表 -->
          <div class="flex space-x-2">
            <button class="px-4 py-1.5 text-blue-600 bg-white rounded-md shadow-sm hover:bg-blue-50 transition-colors whitespace-nowrap">
              应用方案
            </button>
            <button class="px-4 py-1.5 text-gray-600 bg-white rounded-md shadow-sm hover:bg-gray-50 transition-colors whitespace-nowrap"
              @click="() => { currentEditIndex = index; showEditDialog = true }">
              编辑方案
            </button>
          </div>
        </div>
        <!-- 压缩方案预期结果 -->
        <p class="text-gray-600">{{ result.exception }}</p>
        
        <!-- 文件列表及压缩方案 -->
        <div class="mt-4 space-y-2">
          <div v-for="file in result.files" :key="file.id" class="flex items-center justify-between p-3 bg-white rounded-md border border-gray-100">
            <div class="flex items-center space-x-3">
              <i class="fas fa-file-archive text-blue-500"></i>
              <div>
                <p class="text-sm font-medium">{{ file.name }}</p>
                <p class="text-xs text-gray-500">{{ file.size }}</p>
              </div>
            </div>
            <span class="text-sm text-blue-600 bg-blue-50 px-2 py-1 rounded">
              {{ file.selectedAlgorithm || '未选择' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- 编辑压缩方案弹窗 -->
  <div v-if="showEditDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg w-[600px] shadow-xl">
      <div class="p-6 border-b border-gray-200">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-medium">编辑压缩方案</h3>
          <button class="text-gray-400 hover:text-gray-600" @click="showEditDialog = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
      <div class="p-6">
        <div class="space-y-4">
          <div v-for="file in aiResults[currentEditIndex].files" :key="file.id" class="p-4 bg-gray-50 rounded-lg">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <i class="fas fa-file-archive text-blue-500"></i>
                <div>
                  <p class="font-medium">{{ file.name }}</p>
                  <p class="text-sm text-gray-500">{{ file.size }}</p>
                </div>
              </div>
              <div class="w-48">
                <div class="relative">
                  <button @click="file.showAlgorithmList = !file.showAlgorithmList"
                    class="w-full px-4 py-2 text-left bg-white border border-gray-300 rounded-lg flex items-center justify-between !rounded-button">
                    <span>{{ file.selectedAlgorithm || '选择算法' }}</span>
                    <i class="fas fa-chevron-down text-gray-400"></i>
                  </button>
                  <div v-if="file.showAlgorithmList"
                    class="absolute w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                    <div class="py-1">
                      <button v-for="algo in compressionAlgorithms" :key="algo.value"
                        @click="selectAlgorithm(file, algo.value)"
                        class="w-full px-4 py-2 text-left hover:bg-gray-50 !rounded-button">
                        {{ algo.label }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="p-6 border-t border-gray-200 flex justify-end space-x-4">
        <button class="px-4 py-2 border border-gray-300 !rounded-button whitespace-nowrap hover:bg-gray-50"
          @click="showEditDialog = false">
          取消
        </button>
        <button class="px-4 py-2 bg-blue-500 text-white !rounded-button whitespace-nowrap hover:bg-blue-600"
          @click="applyCompressionSettings">
          确定
        </button>
      </div>
    </div>
  </div>
</template>
<script lang="ts" setup>
import { ref, onUnmounted } from 'vue';
import apiService from '../api/apiService';
import { ElMessageBox } from 'element-plus';
import store from '@/store'; 

const fileInput = ref<HTMLInputElement | null>(null);
const showEditDialog = ref(false);
const currentEditIndex = ref(0);

// 控制图标旋转状态
const aiPanelShow =ref(false)
const thinkShow = ref(false)
const isThinking = ref(false);
const analyzeShow = ref(false)
const isAnalyzing = ref(false);
const generatShow = ref(false);
const isGenerating = ref(false);
const compressionAlgorithms = [
  { value: 'zstd', label: 'Zstandard (高压缩比)' },
  { value: 'lzma2', label: 'LZMA2 (超高压缩比)' },
  { value: 'lz4', label: 'LZ4 (快速压缩)' },
  { value: 'deflate', label: 'Deflate (通用压缩)' },
  { value: 'bzip2', label: 'BZip2 (高压缩比)' },
  { value: 'bzip2', label: 'BZip2 (高压缩比)' }
];
const fileList = ref<FileItem[]>([]);
const currentTaskId = ref('');
const aiResults = ref<AiResult[]>([

]);



interface AiResult {
  title: string;
  exception: string;
  files: FileItem[];
}

interface FileItem {
  id: string;
  name: string;
  size: string;
  progress?: number;
  status?: 'pending' | 'uploading' | 'success' | 'failed';
  showAlgorithmList?: boolean;
  selectedAlgorithm?: string;
  file?: File;
}

// 组件逻辑将在这里实现
const generateCompressionPlan = async () => {
  if (fileList.value.length === 0) return;

  if (!currentTaskId.value) {
    currentTaskId.value = crypto.randomUUID();
  }

  // 更新所有文件状态为上传中
  fileList.value.forEach(file => {
    file.status = 'uploading';
    file.progress = 0;
  });
  
  // 批量上传文件
  const uploadPromises = fileList.value.map(file => {
    return apiService.uploadFile(
      {
        file: file.file,
        task_id: currentTaskId.value
      },
      {},
      {},
      {},
      {
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            file.progress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
          }
        }
      }
    ).then(response => {
      if (response.success) {
        file.status = 'success';
      } else {
        file.status = 'failed';
      }
      return response;
    }).catch(error => {
      file.status = 'failed';
      throw error;
    });
  });

  try {
    await Promise.all(uploadPromises);

    // 清空之前的分析结果
    streamText.value = '';
    aiResults.value = []
    generatShow.value = false
    isGenerating.value = false
    thinkShow.value = true
    isStreaming.value = false;
    isThinking.value = true
    
    // 创建EventSource连接

    const userId = store.state.user?.id || '';
    const eventSource = new EventSource(`/api/compression/analyze/?task_id=${currentTaskId.value}&user_id=${userId}`);
    eventSource.onmessage = (event) => {
      isStreaming.value = true
      isThinking.value = false
      isAnalyzing.value=true
      const data = JSON.parse(event.data);
      streamText.value = data.think;
      if (data.think_over){
        isThinking.value = false
        generatShow.value = true
        isGenerating.value = true
      }

      if (data.aiResults){
        aiResults.value = data.aiResults
      }

      if (data.aiResultsOver){
        isGenerating.value = false
      }
      
    };

    eventSource.onerror = () => {
      isStreaming.value = false;
      eventSource.close();
    };

  } catch (error) {
    console.error('文件上传失败:', error);
  }
};

// 选择压缩算法
const selectAlgorithm = (file: any, algorithm: string) => {
  file.selectedAlgorithm = algorithm;
  file.showAlgorithmList = false;
};
// 应用压缩设置
const applyCompressionSettings = () => {
  // 这里可以处理压缩设置的保存逻辑
  showEditDialog.value = false;
  // 重置下拉列表状态
  fileList.value.forEach(file => {
    file.showAlgorithmList = false;
  });
};



const triggerFileInput = () => {
  fileInput.value?.click();
};
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    if (!currentTaskId.value) {
      currentTaskId.value = crypto.randomUUID();
    }

    Array.from(target.files).forEach(file => {
      fileList.value.push({
        id: Math.random().toString(36).substring(2, 9),
        name: file.name,
        size: formatFileSize(file.size),
        progress: 0,
        status: 'pending',
        file
      });
    });
  }
};

const handleDrop = (event: DragEvent) => {
  event.preventDefault();
  const files = event.dataTransfer?.files;
  if (files && files.length > 0) {
    if (!currentTaskId.value) {
      currentTaskId.value = crypto.randomUUID();
    }

    Array.from(files).forEach(file => {
      fileList.value.push({
        id: Math.random().toString(36).substring(2, 9),
        name: file.name,
        size: formatFileSize(file.size),
        progress: 0,
        status: 'pending',
        file
      });
    });
  }
};

const removeFile = async (id: string) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个文件吗？',
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    fileList.value = fileList.value.filter(file => file.id !== id);
    if (fileList.value.length === 0) {
      currentTaskId.value = '';
    }
  } catch {
    // 用户点击取消
  }
};

const clearFileList = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有文件吗？',
      '确认清空',
      {
        confirmButtonText: '清空',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    fileList.value = [];
    currentTaskId.value = '';
  } catch {
    // 用户点击取消
  }
};

const streamText = ref('');
const isStreaming = ref(false);
let streamInterval: number | null = null;
const startStreamText = () => {
  if (isStreaming.value) return;
  isStreaming.value = true;
  isAnalyzing.value = true
  streamText.value = '';
  const fullText = `🤖 **SC-Pro 智能压缩系统** | 版本 2.1.5
基于深度学习的自适应压缩引擎
▌系统特性
⚙️ 智能算法矩阵
• 动态分析文件结构（文档/图像/代码优先策略）
• 多目标优化：体积↓35-78% | 解压速度↑200%
• 异常格式自动转换（支持47种格式互转）

▌操作协议
1️⃣ [输入] 拖放文件至检测区（≤8TB）
2️⃣ [诊断] 自动生成压缩方案报告
3️⃣ [执行] 点击▼启动智能优化`;

  let currentIndex = 0;
  streamInterval = window.setInterval(() => {
    if (currentIndex < fullText.length) {
      streamText.value += fullText[currentIndex];
      currentIndex++;
    } else {
      if (streamInterval) {
        clearInterval(streamInterval);
        streamInterval = null;
      }
      isStreaming.value = false;
    }
  }, 20);
};
startStreamText();
onUnmounted(() => {
  if (streamInterval) {
    clearInterval(streamInterval);
  }
});

</script>
<style scoped></style>
