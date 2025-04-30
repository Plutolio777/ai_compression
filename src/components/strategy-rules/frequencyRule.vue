<template>
  <div class="space-y-4">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
      <div class="frequency-form-item">
        <label class="block text-sm font-medium text-gray-700 mb-2">使用频率</label>
        <div class="frequency-radio-group">
          <button
            v-for="option in frequencyOptions"
            :key="option.value"
            @click="modelValue.frequency = option.value; handleFrequencyChange(option.value)"
            :class="[
              'flex items-center justify-center px-3 py-1.5 rounded-md border',
              'min-w-[70px] text-sm whitespace-nowrap',
              modelValue.frequency === option.value 
                ? 'bg-blue-50 border-blue-200 text-blue-600'
                : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'
            ]"
          >
            <i :class="['fas', option.icon, 'mr-1']"></i>
            <span>{{ option.label }}</span>
          </button>
        </div>
      </div>

        <div class="relative dropdown-container">
        <label class="block text-sm font-medium text-gray-700 mb-2">推荐算法</label>
        <div class="relative">
          <button 
            @click.stop="showAlgorithmList = !showAlgorithmList"
            class="w-full flex items-center justify-between px-3 py-1.5 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 h-[32px] bg-white"
          >
            <span>{{ getAlgorithmLabel(modelValue.algorithm) }}</span>
            <i class="fas fa-chevron-down text-gray-400 text-xs"></i>
          </button>
          <div 
            v-if="showAlgorithmList"
            class="absolute z-[9999] mt-1 w-full bg-white border border-gray-200 rounded-md shadow-lg overflow-visible"
            style="transform: translateY(0);"
          >
            <button
              v-for="algo in algorithms"
              :key="algo.value"
              @click.stop="modelValue.algorithm = algo.value; showAlgorithmList = false"
              class="w-full px-3 py-2 text-left hover:bg-blue-50 flex items-center"
            >
              <span>{{ algo.label }}</span>
              <i 
                v-if="modelValue.algorithm === algo.value"
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
import { ref, onMounted, onUnmounted } from 'vue';
const modelValue = defineModel()  // 自动建立 v-model 绑定
const showAlgorithmList = ref(false);

// 点击外部关闭下拉菜单
const clickOutsideHandler = (event) => {
  const dropdown = event.target.closest('.dropdown-container');
  if (!dropdown && showAlgorithmList.value) {
    showAlgorithmList.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', clickOutsideHandler);
});

onUnmounted(() => {
  document.removeEventListener('click', clickOutsideHandler);
});

const algorithms = [
  { value: 'zip', label: 'ZIP' },
  { value: 'gzip', label: 'GZIP' },
  { value: 'bz2', label: 'BZ2' },
  { value: 'lzma', label: 'LZMA' }
];

const getAlgorithmLabel = (value) => {
  return algorithms.find(a => a.value === value)?.label || '选择算法';
};



const frequencyOptions = ref([
  { value: 'high', label: '高频', icon: 'fa-bolt' },
  { value: 'medium', label: '中频', icon: 'fa-chart-line' },
  { value: 'low', label: '低频', icon: 'fa-clock' }
])

const handleFrequencyChange = (val) => {
  switch(val) {
    case 'high':
      modelValue.algorithm = 'zip'
      break
    case 'medium':
      modelValue.algorithm = 'gzip'
      break
    case 'low':
      modelValue.algorithm = 'lzma'
      break
  }
}
</script>

<style scoped>
.frequency-form-item {
  @apply mb-4;
}

.frequency-radio-group {
  @apply flex gap-2;
}

.frequency-radio-group .fas {
  @apply text-sm mr-1;
}

/* 紧凑模式样式 */
.frequency-radio-group.compact {
  @apply gap-1;
}

.frequency-radio-group.compact button {
  @apply min-w-[40px] p-1;
}

.frequency-radio-group.compact .text {
  @apply hidden;
}

.frequency-radio-group.compact .fas {
  @apply text-lg;
}
</style>
