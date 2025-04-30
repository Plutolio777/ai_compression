<template>
  <div class="bg-white p-6 rounded-xl shadow-lg transition-all hover:shadow-xl">
    <div class="flex items-center space-x-4">
      <div :class="color" class="p-3 rounded-lg">
        <i :class="icon" class="text-xl text-blue-500"></i>
      </div>
      <div>
        <div class="text-gray-500 text-sm">{{ title }}</div>
        <div class="text-3xl font-bold">{{ value }}</div>
      </div>
    </div>
    <div class="mt-4 text-sm text-gray-500">{{ desc }}</div>
  </div>
</template>

<script lang="ts" setup>
defineProps({
  icon: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  value: {
    type: String,
    required: true
  },
  desc: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: 'bg-blue-100'
  }
})
</script>
