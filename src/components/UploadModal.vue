  <template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl">
      <!-- 头部 -->
      <div class="border-b px-6 py-4 flex justify-between items-center">
        <h3 class="text-lg font-medium">上传文件</h3>
        <button @click="close" class="text-gray-500 hover:text-gray-700">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- 主体 -->
      <div class="p-6">
  <!-- 当前路径 -->
  <div v-if="parentId" class="mb-4 text-sm text-gray-600">
    当前文件夹ID: {{ parentId }}
  </div>

        <!-- 拖放区域 -->
        <div 
          @dragover.prevent="dragover = true"
          @dragleave="dragover = false"
          @drop.prevent="handleDrop"
          @click="fileInput?.click()"
          :class="{'border-blue-500 bg-blue-50': dragover}"
          class="border-2 border-dashed rounded-lg p-8 text-center mb-6 cursor-pointer transition-colors hover:border-blue-400"
        >
          <i class="fas fa-cloud-upload-alt text-4xl text-blue-500 mb-2"></i>
          <p class="text-gray-600">点击或拖放文件到此处</p>
          <input 
            type="file" 
            ref="fileInput"
            multiple
            @change="handleFileSelect"
            class="hidden"
          >
        </div>

        <!-- 文件列表 -->
        <div class="border rounded-lg overflow-hidden">
          <div class="grid grid-cols-12 bg-gray-100 p-3 text-sm font-medium text-gray-600">
            <div class="col-span-6">文件名</div>
            <div class="col-span-2">大小</div>
            <div class="col-span-3">进度</div>
            <div class="col-span-1">操作</div>
          </div>
          <div class="divide-y">
            <div 
              v-for="file in files" 
              :key="file.id"
              class="grid grid-cols-12 p-3 items-center text-sm"
            >
              <div class="col-span-6 truncate">{{ file.name }}</div>
              <div class="col-span-2">{{ formatFileSize(file.size) }}</div>
              <div class="col-span-3">
                <div class="w-full bg-gray-200 rounded-full h-2.5">
                  <div 
                    class="bg-blue-600 h-2.5 rounded-full" 
                    :style="{width: `${file.progress}%`}"
                  ></div>
                </div>
                <div class="text-xs mt-1 text-gray-500">
                  {{ file.progress }}% {{ file.status === 'error' ? '上传失败' : '' }}
                </div>
              </div>
              <div class="col-span-1 text-center">
                <button 
                  v-if="file.status === 'error'"
                  @click="retryUpload(file)"
                  class="text-blue-500 hover:text-blue-700"
                >
                  <i class="fas fa-redo"></i>
                </button>
                <button 
                  v-if="file.status !== 'uploading'"
                  @click="removeFile(file.id)"
                  class="text-red-500 hover:text-red-700 ml-2"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部 -->
      <div class="border-t px-6 py-4 flex justify-end space-x-3">
        <button 
          @click="close"
          class="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50"
        >
          取消
        </button>
        <button 
          @click="startUpload"
          :disabled="uploading || files.length === 0"
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-blue-300"
        >
          {{ uploading ? '上传中...' : '开始上传' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import apiService from '../api/apiService'

declare global {
  interface Window {
    uploadedFiles?: Array<{name: string, size: number}>
  }
}

interface UploadFile {
  id: string
  name: string
  size: number
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'done' | 'error'
}

const props = defineProps({
  show: Boolean,
  parentId: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['close', 'upload-success'])

const files = ref<UploadFile[]>([])
const dragover = ref(false)
const uploading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const close = () => {
  if (!uploading.value) {
    files.value = []
    emit('close')
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    addFiles(Array.from(input.files))
    input.value = ''
  }
}

const handleDrop = (e: DragEvent) => {
  dragover.value = false
  if (e.dataTransfer && e.dataTransfer.files.length > 0) {
    addFiles(Array.from(e.dataTransfer.files))
  }
}

const addFiles = (newFiles: File[]) => {
  const MAX_SIZE = 100 * 1024 * 1024 // 100MB
  
  newFiles.forEach(file => {
    if (file.size > MAX_SIZE) {
      alert(`文件 ${file.name} 超过100MB大小限制`)
      return
    }
    
    files.value.push({
      id: crypto.randomUUID(),
      name: file.name,
      size: file.size,
      file,
      progress: 0,
      status: 'pending'
    })
  })
}

const removeFile = (id: string) => {
  files.value = files.value.filter(f => f.id !== id)
}

const retryUpload = (file: UploadFile) => {
  file.progress = 0
  file.status = 'pending'
  startUpload()
}

const startUpload = async () => {
  if (uploading.value || files.value.length === 0) return
  
  // 存储上传的文件信息供Files.vue使用
  window.uploadedFiles = files.value.map(f => ({
    name: f.name,
    size: f.size
  }));
  
  uploading.value = true
  const pendingFiles = files.value.filter(f => f.status === 'pending')
  
  for (const file of pendingFiles) {
    try {
      file.status = 'uploading'
      await uploadFile(file)
      file.status = 'done'
    } catch (error) {
      file.status = 'error'
      console.error('上传失败:', error)
    }
  }
  
  uploading.value = false
  emit('upload-success')
}

    const uploadFile = async (file: UploadFile) => {
        const uploadData = {
            file: file.file
        }
        
        if (props.parentId) {
            uploadData.parent_id = props.parentId
        }
        
        try {
            const response = await apiService.uploadFile(
                uploadData,
                {}, // query params
                {}, // path params
                {}, // headers
                {
                    onUploadProgress: (progressEvent) => {
                        if (progressEvent.total) {
                            file.progress = Math.round(
                                (progressEvent.loaded * 100) / progressEvent.total
                            )
                        }
                    }
                }
            )
            
            if (!response.success) {
                const errorMsg = response.error || '上传失败'
                showToast(errorMsg, 'error')
                throw new Error(errorMsg)
            }
            return response.data
        } catch (error) {
            const errorMsg = error.response?.data?.error || error.message || '上传失败'
            showToast(errorMsg, 'error')
            console.error('上传失败:', error)
            throw error
        }
}
</script>
