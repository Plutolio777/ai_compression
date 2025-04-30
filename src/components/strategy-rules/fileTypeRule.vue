<template>
  <div class="space-y-4">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">文件类型</label>
        <div class="relative">
          <input
            ref="inputRef"
            v-model="model.fileTypes"
            placeholder="输入文件扩展名,用逗号分隔"
            class="w-full px-3 py-1.5 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 h-[32px]"
          />
          <button 
            v-if="model.fileTypes"
            @click="model.fileTypes = ''"
            class="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>

      <div class="relative">
        <label class="block text-sm font-medium text-gray-700 mb-2">推荐算法</label>
        <div class="relative">
          <button 
            @click.stop="showAlgorithmList = !showAlgorithmList"
            class="w-full flex items-center justify-between px-3 py-1.5 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white h-[32px]"
          >
            <span>{{ getAlgorithmLabel(model.algorithm) }}</span>
            <i class="fas fa-chevron-down text-gray-400 text-xs"></i>
          </button>
          <div 
            v-if="showAlgorithmList"
            class="absolute z-[9999] mt-1 w-full bg-white border border-gray-200 rounded-md shadow-lg overflow-visible"
          >
            <button
              v-for="algo in algorithms"
              :key="algo.value"
              @click.stop="model.algorithm = algo.value; showAlgorithmList = false"
              class="w-full px-3 py-2 text-left hover:bg-blue-50 flex items-center"
            >
              <span>{{ algo.label }}</span>
              <i 
                v-if="model.algorithm === algo.value"
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
import { ref, watch, toRaw, defineModel  } from 'vue'
console.log("子组件重载")
const showAlgorithmList = ref(false)
const inputRef = ref(null)

const model = defineModel()  // 自动建立 v-model 绑定



const algorithms = [
  { value: 'zip', label: 'ZIP' },
  { value: 'gzip', label: 'GZIP' },
  { value: 'bz2', label: 'BZ2' }
]

const getAlgorithmLabel = (value) => {
  return algorithms.find(a => a.value === value)?.label || '选择算法'
}

</script>

<style scoped>
/* 保持与frequencyRule一致的样式 */
</style>
