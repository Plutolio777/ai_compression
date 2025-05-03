<template>
  <div class="tag-selector-modal p-4 w-80 bg-white rounded-lg shadow-xl border border-gray-200">
    <!-- 标题和操作区域 -->
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-lg font-semibold text-gray-800">标签管理</h3>
      <button 
        @click="emit('close')"
        class="text-gray-400 hover:text-gray-600 transition-colors"
      >
        <i class="fas fa-times"></i>
      </button>
    </div>

    <!-- 已选标签区域 -->
    <div class="mb-4">
      <h4 class="text-sm font-medium text-gray-500 mb-2">已选标签</h4>
      <div 
        v-if="selectedTags.length > 0"
        class="flex flex-wrap gap-2 p-2 bg-gray-50 rounded-lg min-h-12"
      >
        <span 
          v-for="tag in selectedTags" 
          :key="tag.id"
          class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium shadow-sm"
          :style="{ 
            backgroundColor: tag.color + '20', 
            color: tag.color,
            border: `1px solid ${tag.color}30`
          }"
        >
          {{ tag.name }}
          <button 
            @click.stop="removeTag(tag.id)"
            class="ml-1.5 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <i class="fas fa-times text-xs"></i>
          </button>
        </span>
      </div>
      <div 
        v-else
        class="p-3 text-center text-gray-400 bg-gray-50 rounded-lg"
      >
        <i class="fas fa-tags mb-1"></i>
        <p class="text-xs">暂无已选标签</p>
      </div>
    </div>

    <!-- 标签搜索和选择 -->
    <div class="relative">
      <div class="relative">
        <input
          type="text"
          v-model="searchQuery"
          @focus="showDropdown = true"
          @blur="handleBlur"
          placeholder="搜索或选择标签..."
          class="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
        />
        <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
      </div>
      
      <!-- 下拉菜单 -->
      <transition
        enter-active-class="transition duration-100 ease-out"
        enter-from-class="transform scale-95 opacity-0"
        enter-to-class="transform scale-100 opacity-100"
        leave-active-class="transition duration-75 ease-in"
        leave-from-class="transform scale-100 opacity-100"
        leave-to-class="transform scale-95 opacity-0"
      >
        <div 
          v-show="showDropdown"
          class="absolute z-20 mt-1 w-full bg-white shadow-xl rounded-lg py-1 text-base ring-1 ring-black ring-opacity-5 focus:outline-none max-h-72 overflow-y-auto custom-scroll"
        >
          <div 
            v-for="tag in filteredTags"
            :key="tag.id"
            @mousedown.prevent="selectTag(tag)"
            class="cursor-pointer select-none relative py-2.5 pl-4 pr-10 hover:bg-blue-50 transition-colors"
            :style="{ color: tag.color }"
          >
            <div class="flex items-center">
              <i class="fas fa-tag mr-3" :style="{ color: tag.color }"></i>
              <div class="flex-1 min-w-0">
                <p class="font-medium truncate">{{ tag.name }}</p>
                <p v-if="tag.description" class="text-xs text-gray-500 truncate">{{ tag.description }}</p>
              </div>
            </div>
          </div>
          <div 
            v-if="filteredTags.length === 0"
            class="px-4 py-6 text-center"
          >
            <i class="fas fa-search text-2xl text-gray-300 mb-2"></i>
            <p class="text-gray-500 text-sm">没有找到匹配的标签</p>
            <button 
              class="mt-3 text-xs text-blue-500 hover:text-blue-600"
              @click.stop="showCreateTag = true"
            >
              <i class="fas fa-plus mr-1"></i>创建新标签
            </button>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<style scoped>
.custom-scroll::-webkit-scrollbar {
  width: 6px;
}
.custom-scroll::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}
.custom-scroll::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}
.custom-scroll::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import apiService from '../api/apiService'

const props = defineProps({
  fileId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['close', 'refresh'])

const allTags = ref([])
const selectedTags = ref([])

// 获取文件标签
const fetchFileTags = async () => {
  try {
    const res = await apiService.getFileTags(
      {},
      {},
      { id: props.fileId }
    )
    if (res.success && Array.isArray(res.data)) {
      selectedTags.value = res.data
    }
  } catch (error) {
    console.error('获取文件标签失败:', error)
  }
}

// 初始化时获取文件标签
onMounted(() => {
  fetchFileTags()
})
const searchQuery = ref('')
const showDropdown = ref(false)

// 获取所有标签
const fetchTags = async () => {
  try {
    const res = await apiService.getAllTags()
    if (res.success && Array.isArray(res.data)) {
      allTags.value = res.data
    } else {
      console.error('获取标签失败或返回数据格式不正确:', res)
      allTags.value = []
    }
  } catch (error) {
    console.error('获取标签出错:', error)
    allTags.value = []
  }
}

// 过滤标签
const filteredTags = computed(() => {
  if (!Array.isArray(allTags.value)) {
    return []
  }
  return allTags.value.filter(tag => 
    tag && tag.id && tag.name &&
    !selectedTags.value.some(t => t && t.id === tag.id) &&
    tag.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

// 选择标签
const selectTag = async (tag) => {
  const res = await apiService.addFileTags(
    { tag_ids: [tag.id] },
    {},
    { id: props.fileId }
  )
  
  if (res.success) {
    selectedTags.value.push(tag)
    emit('refresh') // 触发父组件刷新文件列表
  }
  searchQuery.value = ''
  showDropdown.value = false
}

// 移除标签
const removeTag = async (tagId) => {
  const res = await apiService.removeFileTag(
    { tag_id: tagId },
    {},
    { id: props.fileId }
  )
  
  if (res.success) {
    selectedTags.value = selectedTags.value.filter(t => t.id !== tagId)
    emit('refresh') // 触发父组件刷新文件列表
  }
}

// 处理blur事件
const handleBlur = () => {
  setTimeout(() => {
    showDropdown.value = false
  }, 200)
}

// 处理外部点击
const handleOutsideClick = (event) => {
  // 右键点击任何地方都关闭
  if (event.button === 2) {
    event.preventDefault()
    emit('close')
    return
  }
  
  // 左键点击组件外部时关闭
  const isInside = event.composedPath().some(el => 
    el.classList && el.classList.contains('tag-selector-modal')
  )
  if (!isInside) {
    emit('close')
  }
}

// 初始化
onMounted(() => {
  fetchTags()
  window.addEventListener('click', handleOutsideClick)
  window.addEventListener('contextmenu', handleOutsideClick)
})

onUnmounted(() => {
  window.removeEventListener('click', handleOutsideClick)
  window.removeEventListener('contextmenu', handleOutsideClick)
})
</script>
