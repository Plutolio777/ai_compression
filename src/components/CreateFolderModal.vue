<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md">
      <!-- 头部 -->
      <div class="border-b px-6 py-4 flex justify-between items-center">
        <h3 class="text-lg font-medium">新建文件夹</h3>
        <button @click="close" class="text-gray-500 hover:text-gray-700">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- 主体 -->
      <div class="p-6">
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">文件夹名称</label>
          <input
            type="text"
            v-model="folderName"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="输入文件夹名称"
            @keyup.enter="createFolder"
          >
          <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
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
          @click="createFolder"
          :disabled="!folderName"
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-blue-300"
        >
          创建
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import apiService from '@/api/apiService'

const props = defineProps({
  show: Boolean,
  currentPath: {
    type: Array as () => string[],
    default: () => []
  }
})

const emit = defineEmits(['close', 'create-success'])

const folderName = ref('')
const error = ref('')

const close = () => {
  folderName.value = ''
  error.value = ''
  emit('close')
}

const createFolder = async () => {
  const name = folderName.value.trim()
  if (!name) {
    error.value = '请输入文件夹名称'
    return
  }

  // 验证文件夹名称
  const invalidChars = /[\\/:*?"<>|]/
  if (invalidChars.test(name)) {
    error.value = '名称不能包含以下字符: \\ / : * ? " < > |'
    return
  }

  if (name.length > 50) {
    error.value = '名称长度不能超过50个字符'
    return
  }

  const reservedNames = ['con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9']
  if (reservedNames.includes(name.toLowerCase())) {
    error.value = '不能使用系统保留名称'
    return
  }

  try {
    const response = await apiService.createFolder({
      name: folderName.value,
      path: props.currentPath.join('/')
    })
    if (response.success) {
      emit('create-success', response.data)
      close()
    } else {
      error.value = response.error || '创建文件夹失败'
    }
  } catch (err) {
    error.value = '创建文件夹失败'
  }
}
</script>
