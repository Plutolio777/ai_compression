<template>
  <div class="strategy-container px-4 py-6 bg-gradient-to-br from-gray-50 to-white relative">
    <div class="max-w-full mx-auto px-4 pt-6">
      <div class="flex justify-between items-center mb-8">
        <h2 class="text-2xl font-semibold text-gray-800">策略配置中心</h2>
        <button @click="saveAllStrategies" class="btn-primary px-6 py-3 text-sm font-medium">
          <i class="fas fa-save mr-2"></i>保存所有策略
        </button>
      </div>
      
      <div class="grid md:grid-cols-2 gap-8">
        <!-- 压缩策略 -->
        <div class="space-y-6">
          <div class="strategy-card">
        <div class="card-header">
          <h3>压缩策略配置</h3>
        </div>
        <div class="card-body">
          <!-- 基本信息 -->
          <div class="mb-6">
            <h4 class="font-medium mb-3 text-gray-700 border-b pb-2">基本信息</h4>
            <div class="space-y-4">
              <div class="space-y-2">
                <label class="block text-sm font-medium text-gray-700">策略名称</label>
                <input v-model="compressionStrategy.name" class="input-field h-9 text-sm rounded-lg">
              </div>
              <div class="space-y-2">
                <label class="block text-sm font-medium text-gray-700">策略描述</label>
                <textarea 
                  v-model="compressionStrategy.description"
                  class="input-field"
                  placeholder="请输入策略描述..."></textarea>
              </div>
            </div>
          </div>

          <!-- 文件类型规则 -->
          <div>
            <div class="flex justify-between items-center mb-3">
              <h4 class="font-medium text-gray-700 border-b pb-2">文件类型规则</h4>
              <!-- <button @click="addRule('fileType')" class="btn-sm btn-primary">
                <i class="fas fa-plus mr-2"></i>添加规则
              </button> -->
            </div>
            
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">策略类型</label>
              <div class="flex flex-wrap gap-2">
                <button v-for="type in strategyTypes" 
                        @click="addRule(type.value)"
                        :class="['px-4 py-2 rounded-lg border', 
                                'hover:bg-blue-50 hover:border-blue-300']">
                  <i :class="['fas', type.icon, 'mr-2']"></i>
                  {{ type.label }}
                </button>
              </div>
            </div>

            <draggable 
              v-model="compressionStrategy.compression.rules"
              :item-key="item => item.uuid"
              handle=".drag-handle"
              class="space-y-4 relative z-0"
            >
              <template #item="{element, index}">
                <div class="rule-card group relative p-4 border border-gray-200 rounded-lg hover:shadow-md transition-all" :key="element.uuid">
                  <div class="flex items-start justify-between">
                    <div class="flex items-center space-x-3">
                      <div class="drag-handle cursor-move pt-1 text-gray-400 hover:text-gray-600">
                        <i class="fas fa-grip-vertical"></i>
                      </div>
                      <div :class="['text-xl', iconMapping[getFileCategory(element.config.fileTypes || '')].color]">
                        <i :class="['fas', strategyTypes.find(t => t.value === element.type)?.icon]"></i>
                      </div>
                      <div>
                        <h5 class="font-medium">{{ element.name }}</h5>
                        <p class="text-sm text-gray-500">{{ strategyTypes.find(t => t.value === element.type)?.label }}</p>
                      </div>
                    </div>
                    <button @click="removeRule(index)" class="text-gray-400 hover:text-red-500">
                      <i class="fas fa-times"></i>
                    </button>
                  </div>
                  
                  <!-- 动态表单区域 -->
                  <div class="mt-4 pt-4 border-t border-gray-100">
                  <component :is="getRuleComponent(element.type)" 
                               v-model="element.config"
                               :key="element.uuid" />
                  </div>
                </div>
              </template>
            </draggable>
          </div>
        </div>
      </div>
    </div>

        <!-- 归档策略 -->
        <div class="space-y-6">
          <div class="strategy-card">
        <div class="card-header">
          <h3>归档策略配置</h3>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-gray-600 mb-1">策略名称</label>
              <input v-model="archiveStrategy.name" class="input-field">
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">策略描述</label>
              <input v-model="archiveStrategy.description" class="input-field">
            </div>
              <div>
              <label class="block text-sm text-gray-600 mb-1">归档格式</label>
              <div class="relative">
                <button @click="showArchiveFormatList = !showArchiveFormatList"
                  class="w-full px-3 py-2 text-left bg-white border border-gray-300 rounded-lg flex items-center justify-between">
                  <span>{{ archiveStrategy.archive.format.toUpperCase() }}</span>
                  <i class="fas fa-chevron-down text-gray-400"></i>
                </button>
                <div v-if="showArchiveFormatList" 
                  class="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg">
                  <button @click="archiveStrategy.archive.format = 'zip'; showArchiveFormatList = false"
                    class="w-full px-3 py-2 text-left hover:bg-gray-50">
                    ZIP
                  </button>
                  <button @click="archiveStrategy.archive.format = 'tar'; showArchiveFormatList = false"
                    class="w-full px-3 py-2 text-left hover:bg-gray-50">
                    TAR
                  </button>
                </div>
              </div>
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">分卷大小(MB)</label>
              <input v-model.number="archiveStrategy.archive.volumeSize" type="number" class="input-field">
            </div>
          </div>
        </div>
      </div>
    </div>

      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, defineAsyncComponent,  shallowRef,  markRaw} from 'vue'
import apiService from '@/api/apiService'
import draggable from 'vuedraggable'

const isDev = import.meta.env.DEV

// 文件类型图标映射
const iconMapping = {
  image: { icon: 'far fa-image', color: 'text-blue-500' },
  document: { icon: 'far fa-file-alt', color: 'text-green-500' },
  video: { icon: 'far fa-file-video', color: 'text-purple-500' },
  audio: { icon: 'far fa-file-audio', color: 'text-yellow-500' },
  archive: { icon: 'far fa-file-archive', color: 'text-red-500' },
  default: { icon: 'far fa-file', color: 'text-gray-500' }
}

// 获取文件类别
const getFileCategory = (fileTypes) => {
  const types = fileTypes.split(',')
  if (types.some(t => ['.jpg','.png','.gif'].includes(t))) return 'image'
  if (types.some(t => ['.pdf','.doc','.docx'].includes(t))) return 'document'
  if (types.some(t => ['.mp4','.mov','.avi'].includes(t))) return 'video'
  if (types.some(t => ['.mp3','.wav','.aac'].includes(t))) return 'audio'
  if (types.some(t => ['.zip','.rar','.7z'].includes(t))) return 'archive'
  return 'default'
}

  // 压缩策略数据模型
  const strategyTypes = [
    { value: 'fileType', label: '文件类型', icon: 'fa-file-alt' },
    { value: 'fileSize', label: '文件大小', icon: 'fa-weight' },
    { value: 'frequency', label: '使用频率', icon: 'fa-chart-line' },
    { value: 'scenario', label: '业务场景', icon: 'fa-briefcase' }
  ]

const compressionStrategy = ref({
  name: '默认压缩策略',
  description: '适用于普通文件的默认压缩策略',
  compression: {
    rules: [
      {
        type: 'fileType',
        
        uuid: crypto.randomUUID(), // 使用更可靠的唯一标识
        name: '图片压缩策略',
        config: {
          fileTypes: '.jpg,.png',
          fileCategory: 'image',
          algorithm: 'zip',
        },
        showAlgorithmList: false
      }
    ]
  }
})

const showArchiveFormatList = ref(false)

// 归档策略数据模型  
const archiveStrategy = ref({
  name: '高效归档策略',
  description: '大文件分卷归档策略',
  archive: {
    format: 'zip',
    volumeSize: 500
  }
})

// 添加规则

const addRule = (type) => {
  const baseRule = {
    uuid: crypto.randomUUID(), // 使用更可靠的唯一标识
    type,
    name: `${strategyTypes.find(t => t.value === type).label}策略`,
    
    config: {

    }
  }

  // 根据类型初始化配置
  switch(type) {
    case 'fileType':
      baseRule.config = { fileTypes: '', fileCategory: '', algorithm: '' }
      break
    case 'fileSize':
      baseRule.config = { sizeRange: 'medium', splitVolume: false , algorithm: ''}
      break
    case 'frequency':
      baseRule.config = { frequency: 'medium' , algorithm: ''}
      break
    case 'scenario':
      baseRule.config = { scenario: 'storage' , algorithm: ''}
      break
  }
  compressionStrategy.value.compression.rules.push(baseRule)
  // compressionStrategy.value = {...compressionStrategy.value}
}

// 移除规则
const removeRule = (index) => {
  compressionStrategy.value.compression.rules.splice(index, 1)
}

// 获取对应类型的组件
const asyncComponentCache = new Map()

const getRuleComponent = (type) => {
  if (!asyncComponentCache.has(type)) {
    asyncComponentCache.set(
      type,
      defineAsyncComponent(() =>
        import(`@/components/strategy-rules/${type}Rule.vue`)
      )
    )
  }
  return asyncComponentCache.get(type)
}

// 保存所有策略
const saveAllStrategies = async () => {
  if (isDev) {
    // 开发环境模拟保存
    console.log('保存策略:', {
      compression: compressionStrategy.value.compression.rules,
      archive: archiveStrategy.value
    })
    return { success: true }
  } else {
    // 生产环境调用API
    const res = await apiService.saveStrategies({
      compression: compressionStrategy.value,
      archive: archiveStrategy.value
    })
    return res
  }
}

// 初始化加载时可以添加一些默认规则
onMounted(() => {
  if (compressionStrategy.value.compression.rules.length === 0) {
    addRule('fileType')
  }
})
</script>

<style scoped>
/* 自定义下拉选项样式 - 类似Element UI风格 */
select {
  @apply appearance-none bg-white rounded border border-gray-300;
  height: 32px;
  line-height: 32px;
  padding: 0 28px 0 12px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

select:hover {
  @apply border-blue-400;
}

select:focus {
  @apply border-blue-500 outline-none ring-1 ring-blue-200;
}

select option {
  @apply py-1 px-3 text-sm text-gray-700;
}

select option:hover {
  @apply bg-blue-50;
}

select option:checked {
  @apply bg-blue-100 text-blue-700 font-medium;
}

/* 下拉箭头样式 */
.select-wrapper {
  @apply relative inline-block;
}

.select-wrapper::after {
  content: "";
  @apply absolute right-2 top-1/2 -translate-y-1/2;
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 5px solid #9ca3af;
  pointer-events: none;
}

/* 禁用状态 */
select:disabled {
  @apply bg-gray-100 cursor-not-allowed opacity-70;
}

/* 页面容器 */
.strategy-container {
  @apply bg-gradient-to-b from-gray-50 to-white min-h-screen;
}

/* 策略卡片 */
.strategy-card {
  @apply bg-white rounded-2xl shadow-lg hover:shadow-xl 
         border border-gray-100 p-8 mb-8 transition-all duration-300
         relative overflow-visible;
  background-image: radial-gradient(circle at 100% 0%, rgba(229, 247, 255, 0.3) 0%, transparent 40%),
                    radial-gradient(circle at 0% 100%, rgba(203, 237, 255, 0.3) 0%, transparent 40%);
}

/* 卡片头部 */
.card-header {
  @apply px-0 py-0 mb-6 flex justify-between items-center border-b border-gray-100 pb-4;
}

.card-header h3 {
  @apply text-xl font-semibold text-gray-800 relative;
}

.card-header h3::before {
  content: "";
  @apply absolute -bottom-1 left-0 w-1/3 h-1 bg-blue-500 rounded-full;
}

/* 策略区域 */
.strategy-section {
  @apply mb-12 transform transition-all duration-500;
}

.strategy-section:hover {
  @apply -translate-y-1;
}

/* 输入框 */
.input-field {
  @apply w-full px-4 py-3 border border-gray-200 rounded-xl 
         focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-400
         bg-white shadow-sm;
}

/* 文本域特殊样式 */
.input-field[type="textarea"],
.input-field[resize-y] {
  transition: height 0.2s ease;
  resize: vertical;
  min-height: 80px;
}

/* 主按钮 */
.btn-primary {
  @apply px-6 py-2 bg-white text-blue-600 rounded-lg border border-blue-200
         hover:bg-blue-50 hover:border-blue-300 transition-colors duration-200
         shadow-none hover:shadow-sm;
}

/* 小按钮 */
.btn-sm {
  @apply px-3 py-1 text-sm rounded-md border border-gray-200 bg-white
         hover:bg-gray-50 transition-colors duration-200;
}

/* 文件规则卡片样式 */
.rule-card {
  @apply bg-white p-6 rounded-xl border border-gray-100 
         hover:border-blue-200 hover:shadow-xl transition-all duration-300
         relative overflow-visible;
  background-image: radial-gradient(circle at 0% 0%, rgba(243, 244, 246, 0.6) 0%, transparent 25%);
}

.rule-card::before {
  content: "";
  @apply absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-blue-400 to-blue-600 opacity-0 transition-opacity duration-300;
}

.rule-card:hover::before {
  @apply opacity-100;
}

/* 拖动手柄 */
.drag-handle {
  @apply cursor-move text-gray-400 hover:text-gray-600 transition-colors duration-200;
}

/* 策略类型按钮 */
.strategy-container button[class*="px-4 py-2 rounded-lg border"] {
  @apply bg-white text-gray-700 border border-gray-200 rounded-lg
         hover:bg-blue-50 hover:text-blue-600 hover:border-blue-200
         transition-colors duration-200 px-4 py-2 text-sm;
}

/* 保存按钮容器 */
.strategy-container .mt-8.flex.justify-end {
  @apply relative;
}

.strategy-container .mt-8.flex.justify-end::before {
  content: "";
  @apply absolute -top-8 left-0 w-full h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent;
}
</style>
