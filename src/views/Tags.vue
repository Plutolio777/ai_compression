<template>
  <div class="px-2 py-3 bg-gray-50 min-h-screen">
    
    <div class="space-y-3">
      <!-- 标题 -->
      <h2 class="text-xl font-bold text-gray-800 px-2">标签管理</h2>

      <!-- 操作栏 -->
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 bg-white p-4 rounded-xl shadow-lg mx-2 border border-gray-100 hover:shadow-xl transition-all duration-300"
           style="background-image: radial-gradient(circle at 100% 0%, rgba(229, 247, 255, 0.3) 0%, transparent 40%),
                  radial-gradient(circle at 0% 100%, rgba(203, 237, 255, 0.3) 0%, transparent 40%)">
        <div class="flex items-center space-x-3">
          <!-- 搜索标签 -->
          <div class="relative w-64">
            <input
              v-model="searchQuery"
              placeholder="搜索标签..."
              class="w-full pl-8 pr-3 py-[0.375rem] border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 text-xs"
            />
            <svg class="absolute left-2 top-1/2 transform -translate-y-1/2 h-3 w-3 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          
          <!-- 颜色搜索 -->
          <div class="relative color-picker-container">
            <div 
              @click.stop="toggleColorPicker"
              class="w-40 pl-3 pr-10 py-[0.25rem] border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 flex items-center cursor-pointer text-xs"
            >
              <span 
                v-if="selectedColor" 
                class="w-4 h-4 rounded-full mr-2" 
                :style="{backgroundColor: selectedColor}"
              ></span>
              <span class="text-sm text-gray-600 flex-grow">
                {{ selectedColor ? '已选择' : '颜色筛选' }}
              </span>
              <svg 
                v-if="selectedColor"
                @click.stop="selectedColor = ''"
                class="absolute right-8 h-4 w-4 text-gray-400 hover:text-gray-600"
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              <svg class="absolute right-2 h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
            
            <div 
              v-if="showColorPicker"
              class="absolute z-10 mt-1 w-40 bg-white rounded-lg shadow-lg border border-gray-200 p-2"
            >
              <div class="grid grid-cols-6 gap-2">
                <div 
                  v-for="color in colorOptions"
                  :key="color"
                  @click="selectedColor = color; showColorPicker = false"
                  class="w-6 h-6 rounded-full cursor-pointer border-2 border-transparent hover:border-gray-300"
                  :style="{backgroundColor: color}"
                  :class="{'border-blue-500': selectedColor === color}"
                ></div>
              </div>
              <div 
                @click="selectedColor = ''; showColorPicker = false"
                class="mt-2 text-sm text-center text-blue-600 cursor-pointer hover:underline"
              >
                清除筛选
              </div>
            </div>
          </div>
        </div>
        
        <button
          @click="openDialog('create')"
          class="px-3 py-1.5 py-[0.25rem] bg-white border border-blue-400 text-blue-600 rounded-lg hover:bg-blue-50 flex items-center text-sm"
        >
          <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          新建标签
        </button>
      </div>

      <!-- 标签表格 -->
      <div class="bg-white rounded-xl shadow-lg overflow-hidden mx-2 border border-gray-100 hover:shadow-xl transition-all duration-300"
           style="background-image: radial-gradient(circle at 100% 0%, rgba(229, 247, 255, 0.3) 0%, transparent 40%),
                  radial-gradient(circle at 0% 100%, rgba(203, 237, 255, 0.3) 0%, transparent 40%)">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gradient-to-r from-gray-50 to-gray-100">
              <tr>
                <th scope="col" class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/5">
                  标签名称
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden md:table-cell">
                  描述
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/6">
                  关联文件
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden sm:table-cell">
                  创建时间
                </th>
                <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  操作
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="row in filteredTags" :key="row.id" class="hover:bg-gray-50/50">
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="flex items-center">
                    <span 
                      class="w-3 h-3 rounded-full mr-2"
                      :style="{backgroundColor: row.color}"
                    ></span>
                    {{ row.name }}
                  </div>
                </td>
                <td class="px-4 py-3 text-gray-500 hidden md:table-cell max-w-[200px]">
                  <div 
                    class="truncate cursor-pointer hover:text-blue-500"
                    @mouseenter="showTooltip($event, row.description || '-')"
                    @mouseleave="hideTooltip"
                  >
                    {{ row.description || '-' }}
                  </div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  {{ row.fileCount }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap hidden sm:table-cell">
                  {{ formatDate(row.createdAt) }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                <div class="flex space-x-4">
                  <button 
                    @click="openDialog('edit', row)"
                    class="text-blue-600 hover:text-blue-900 flex items-center"
                  >
                    <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    编辑
                  </button>
                  <button 
                    @click="handleDelete(row)"
                    class="text-red-600 hover:text-red-900 flex items-center"
                  >
                    <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    删除
                  </button>
                </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 分页 -->
      <div class="mt-4 flex items-center justify-between mx-2 px-2">
        <div class="text-sm text-gray-500">
          共 {{ pagination.total }} 条记录
        </div>
        <div class="flex space-x-2">
          <button
            @click="pagination.page = Math.max(1, pagination.page - 1)"
            :disabled="pagination.page === 1"
            class="px-3 py-1 border rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            上一页
          </button>
          <div class="flex space-x-1">
            <button
              v-for="page in Math.ceil(pagination.total / pagination.pageSize)"
              :key="page"
              @click="pagination.page = page"
              class="w-8 h-8 rounded-md flex items-center justify-center"
              :class="{
                'bg-blue-600 text-white': page === pagination.page,
                'text-gray-700 hover:bg-gray-50': page !== pagination.page
              }"
            >
              {{ page }}
            </button>
          </div>
          <button
            @click="pagination.page = Math.min(Math.ceil(pagination.total / pagination.pageSize), pagination.page + 1)"
            :disabled="pagination.page === Math.ceil(pagination.total / pagination.pageSize)"
            class="px-3 py-1 border rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一页
          </button>
        </div>
      </div>

      <!-- 表单弹窗 -->
      <div v-if="dialogVisible" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg shadow-xl w-full max-w-md">
          <div class="px-6 py-4 border-b">
            <h3 class="text-lg font-medium text-gray-900">
              {{ isEdit ? '编辑' : '新建' }}标签
            </h3>
          </div>
          
          <div class="px-6 py-4 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">标签名称</label>
              <input
                v-model="form.name"
                placeholder="请输入标签名称"
                maxlength="20"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div class="text-xs text-gray-500 mt-1">
                {{ form.name.length }}/20
              </div>
              <div v-if="!form.name" class="text-xs text-red-500 mt-1">
                请输入标签名称
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">标签描述</label>
              <textarea
                v-model="form.description"
                placeholder="请输入标签描述"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="3"
              ></textarea>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">标签颜色</label>
              <div class="grid grid-cols-6 gap-2">
                <div
                  v-for="color in colorOptions"
                  :key="color"
                  class="w-8 h-8 rounded-full cursor-pointer border-2"
                  :class="{ 'border-blue-500': form.color === color }"
                  :style="{backgroundColor: color}"
                  @click="form.color = color"
                ></div>
              </div>
            </div>
          </div>
          
          <div class="px-6 py-4 border-t flex justify-end space-x-3">
            <button
              @click="dialogVisible = false"
              class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              取消
            </button>
            <button
              @click="submitForm"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {{ isEdit ? '保存修改' : '创建标签' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 描述弹窗 -->
    <div 
      v-if="tooltipVisible"
      class="fixed z-50 bg-white shadow-lg rounded-md p-3 border border-gray-200 max-w-xs pointer-events-none whitespace-normal break-words max-h-60 overflow-y-auto"
      :style="{
        left: `${Math.min(tooltipPosition.x + 10, windowWidth - 250)}px`,
        top: `${Math.min(tooltipPosition.y + 10, windowHeight - 200)}px`
      }"
    >
      {{ tooltipContent }}
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="deleteConfirmVisible" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md">
        <div class="px-6 py-4 border-b">
          <h3 class="text-lg font-medium text-gray-900">确认删除</h3>
        </div>
        <div class="px-6 py-4">
          <p>确定要删除该标签吗？此操作不可撤销。</p>
        </div>
        <div class="px-6 py-4 border-t flex justify-end space-x-3">
          <button
            @click="deleteConfirmVisible = false"
            class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            取消
          </button>
          <button
            @click="confirmDelete"
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            确认删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted } from 'vue'
import apiService from '@/api/apiService'

interface Tag {
  id: string
  name: string
  description: string
  color: string
  fileCount: number
  createdAt: string
}

// 颜色预设选项
const colorOptions = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD',
  '#FF9999', '#7DCEA0', '#F9E79F', '#D2B4DE', '#A9CCE3',
  '#F5B7B1', '#AED6F1'
]

// 状态管理
const tags = ref<Tag[]>([])
const searchQuery = ref('')
const selectedColor = ref('')
const showColorPicker = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const tooltipVisible = ref(false)
const tooltipContent = ref('')
const tooltipPosition = reactive({ x: 0, y: 0 })

// 点击外部关闭颜色选择器
const closeColorPicker = (e: MouseEvent) => {
  const target = e.target as HTMLElement
  if (!target.closest('.color-picker-container')) {
    showColorPicker.value = false
    document.removeEventListener('click', closeColorPicker)
  }
}

const toggleColorPicker = () => {
  showColorPicker.value = !showColorPicker.value
  if (showColorPicker.value) {
    setTimeout(() => {
      document.addEventListener('click', closeColorPicker)
    }, 0)
  }
}

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const form = reactive({
  id: '',
  name: '',
  description: '',
  color: colorOptions[0]
})

// 计算属性
const filteredTags = computed(() => {
  return tags.value.filter(tag => {
    const matchSearch = tag.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchColor = selectedColor.value ? tag.color === selectedColor.value : true
    return matchSearch && matchColor
  })
})

// 方法
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const openDialog = (type: 'create' | 'edit', row?: Tag) => {
  isEdit.value = type === 'edit'
  if (isEdit.value && row) {
    Object.assign(form, row)
  } else {
    form.id = ''
    form.name = ''
    form.color = colorOptions[0]
  }
  dialogVisible.value = true
}

const showToast = (message: string, type: 'success' | 'error' = 'success') => {
  const toast = document.createElement('div')
  toast.className = `fixed top-4 right-4 px-4 py-2 rounded-md shadow-lg text-white ${
    type === 'success' ? 'bg-green-500' : 'bg-red-500'
  }`
  toast.textContent = message
  document.body.appendChild(toast)
  
  setTimeout(() => {
    toast.remove()
  }, 3000)
}

const submitForm = async () => {
  if (!form.name) {
    showToast('请输入标签名称', 'error')
    return
  }
  
  if (form.name.length > 20) {
    showToast('名称长度不能超过20个字符', 'error')
    return
  }

  try {
    if (isEdit.value) {
      // 更新标签
      const result = await apiService.updateTag(
        form,
        {},
        {id: form.id}
      )
      if (result.success) {
        const index = tags.value.findIndex(t => t.id === form.id)
        tags.value.splice(index, 1, result.data)
        showToast('标签更新成功')
      } else {
        showToast(result.error || '更新失败', 'error')
      }
    } else {
      // 创建标签
      const result = await apiService.createTag(form)
      if (result.success) {
        tags.value.unshift(result.data)
        showToast('标签创建成功')
      } else {
        showToast(result.error || '创建失败', 'error')
      }
    }
  } catch (error) {
    showToast('请求出错: ' + error.message, 'error')
  }
  
  dialogVisible.value = false
}

const showTooltip = (event: MouseEvent, content: string) => {
  tooltipContent.value = content
  tooltipPosition.x = event.clientX
  tooltipPosition.y = event.clientY
  tooltipVisible.value = true
}

const hideTooltip = () => {
  tooltipVisible.value = false
}

const windowWidth = ref(window.innerWidth)
const windowHeight = ref(window.innerHeight)
const deleteConfirmVisible = ref(false)
const deletingTag = ref<Tag | null>(null)

// 监听窗口大小变化
onMounted(() => {
  window.addEventListener('resize', () => {
    windowWidth.value = window.innerWidth
    windowHeight.value = window.innerHeight
  })
})

const handleDelete = (row: Tag) => {
  deletingTag.value = row
  deleteConfirmVisible.value = true
}

const confirmDelete = async () => {
  if (!deletingTag.value) return
  
  try {
    const result = await apiService.deleteTag(
      {},
      {},
      {id: deletingTag.value.id}
    )
    if (result.success) {
      tags.value = tags.value.filter(t => t.id !== deletingTag.value?.id)
      showToast('删除成功')
    } else {
      showToast(result.error || '删除失败', 'error')
    }
  } catch (error) {
    showToast('请求出错: ' + error.message, 'error')
  }
  
  deleteConfirmVisible.value = false
  deletingTag.value = null
}

// 获取标签数据
onMounted(async () => {
  try {
    const result = await apiService.getTags()
    if (result.success) {
      tags.value = result.data.results
      pagination.total = result.data.count
    } else {
      showToast(result.error || '获取标签失败', 'error')
    }
  } catch (error) {
    showToast('请求出错: ' + error.message, 'error')
  }
})
</script>
