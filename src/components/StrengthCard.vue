<template>
  <div class="bg-white rounded-xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 group">
    <div class="w-16 h-16 mb-6 rounded-lg flex items-center justify-center text-3xl" 
         :class="iconBgColor">
      <i :class="icon"></i>
    </div>
    <h3 class="text-xl font-bold mb-3">{{ title }}</h3>
    <p class="text-gray-600 mb-4">{{ description }}</p>
    <div class="mt-auto pt-4 border-t border-gray-100">
      <a href="#" class="text-blue-600 hover:text-blue-800 flex items-center group-hover:underline">
        了解更多
        <i class="fas fa-arrow-right ml-2 text-sm"></i>
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  icon: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true  
  },
  description: {
    type: String,
    required: true
  },
  iconBgColor: {
    type: String,
    default: 'bg-blue-100 text-blue-600'
  }
})
</script>
