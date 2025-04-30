<template>
  <div class="space-y-4">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">文件大小范围</label>
        <div class="relative">
          <button 
            @click.stop="showSizeRangeList = !showSizeRangeList"
            class="w-full flex items-center justify-between px-3 py-1.5 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white h-[32px]"
          >
            <span>{{ getSizeRangeLabel(localValue.sizeRange) }}</span>
            <i class="fas fa-chevron-down text-gray-400 text-xs"></i>
          </button>
          <div 
            v-if="showSizeRangeList"
            class="absolute z-[9999] mt-1 w-full bg-white border border-gray-200 rounded-md shadow-lg overflow-visible"
          >
            <button
              v-for="range in sizeRanges"
              :key="range.value"
              @click.stop="handleSizeRangeSelect(range.value)"
              class="w-full px-3 py-2 text-left hover:bg-blue-50 flex items-center"
            >
              <span>{{ range.label }}</span>
              <i 
                v-if="localValue.sizeRange === range.value"
                class="fas fa-check ml-auto text-blue-500"
              ></i>
            </button>
          </div>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">推荐算法</label>
        <div class="relative">
          <button 
            @click.stop="showAlgorithmList = !showAlgorithmList"
            class="w-full flex items-center justify-between px-3 py-1.5 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white h-[32px]"
          >
            <span>{{ getAlgorithmLabel(localValue.algorithm) }}</span>
            <i class="fas fa-chevron-down text-gray-400 text-xs"></i>
          </button>
          <div 
            v-if="showAlgorithmList"
            class="absolute z-[9999] mt-1 w-full bg-white border border-gray-200 rounded-md shadow-lg overflow-visible"
          >
            <button
              v-for="algo in algorithms"
              :key="algo.value"
              @click.stop="handleAlgorithmSelect(algo.value)"
              class="w-full px-3 py-2 text-left hover:bg-blue-50 flex items-center"
            >
              <span>{{ algo.label }}</span>
              <i 
                v-if="localValue.algorithm === algo.value"
                class="fas fa-check ml-auto text-blue-500"
              ></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { watch, ref } from 'vue'

const showSizeRangeList = ref(false)
const showAlgorithmList = ref(false)
const localValue = ref()

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
})

const emit = defineEmits(['update:modelValue'])
localValue.value = {...props.modelValue} || {}

const sizeRanges = [
  { value: 'small', label: '小文件 (<1MB)' },
  { value: 'medium', label: '中等文件 (1MB-10MB)' },
  { value: 'large', label: '大文件 (>10MB)' }
]

const algorithms = [
  { value: 'zip', label: 'ZIP' },
  { value: 'gzip', label: 'GZIP' },
  { value: 'bz2', label: 'BZ2' },
  { value: 'lzma', label: 'LZMA' }
]

const getSizeRangeLabel = (value) => {
  return sizeRanges.find(r => r.value === value)?.label || '选择文件大小范围'
}

const getAlgorithmLabel = (value) => {
  return algorithms.find(a => a.value === value)?.label || '选择算法'
}

const handleSizeRangeSelect = (value) => {
  localValue.value = { 
    ...localValue.value, 
    sizeRange: value
  }
  emit('update:modelValue', localValue.value)
  showSizeRangeList.value = false
  
  // 根据文件大小自动推荐算法
  switch(value) {
    case 'small':
      localValue.value.algorithm = 'zip'
      break
    case 'medium':
      localValue.value.algorithm = 'gzip'
      break
    case 'large':
      localValue.value.algorithm = 'lzma'
      break
  }
}

const handleAlgorithmSelect = (value) => {
  localValue.value = { 
    ...localValue.value, 
    algorithm: value
  }
  emit('update:modelValue', localValue.value)
  showAlgorithmList.value = false
}
</script>
