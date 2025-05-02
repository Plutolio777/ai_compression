<template>
  <div class="tag-selector-modal">
    <!-- 标签选择器 -->
    <div class="flex flex-wrap gap-2 mb-2">
      <span 
        v-for="tag in selectedTags" 
        :key="tag.id"
        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
        :style="{ backgroundColor: tag.color + '20', color: tag.color }"
      >
        {{ tag.name }}
        <button 
          @click.stop="removeTag(tag.id)"
          class="ml-1 text-gray-400 hover:text-gray-600"
        >
          &times;
        </button>
      </span>
    </div>

    <!-- 下拉选择框 -->
    <div class="relative">
      <input
        type="text"
        v-model="searchQuery"
        @focus="showDropdown = true"
        @blur="handleBlur"
        placeholder="选择标签..."
        class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
      />
      
      <!-- 下拉菜单 -->
      <div 
        v-show="showDropdown"
        class="absolute z-10 mt-1 w-full bg-white shadow-lg rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 focus:outline-none max-h-60 overflow-auto"
      >
        <div 
          v-for="tag in filteredTags"
          :key="tag.id"
          @mousedown.prevent="selectTag(tag)"
          class="cursor-pointer select-none relative py-2 pl-3 pr-9 hover:bg-gray-100"
          :style="{ color: tag.color }"
        >
          <div class="flex items-center">
            <span class="font-medium">{{ tag.name }}</span>
            <span class="ml-2 text-xs text-gray-500">{{ tag.description }}</span>
          </div>
        </div>
        <div 
          v-if="filteredTags.length === 0"
          class="px-3 py-2 text-gray-500 text-sm"
        >
          没有匹配的标签
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import apiService from '../api/apiService'

const props = defineProps({
  fileId: {
    type: Number,
    required: true
  },
  initialTags: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:tags'])

const allTags = ref([])
const selectedTags = ref([...props.initialTags])
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
    emit('update:tags', [...selectedTags.value])
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
    emit('update:tags', [...selectedTags.value])
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
