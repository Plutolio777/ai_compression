<template>
  <div class="flex items-center justify-center p-4 border rounded-lg hover:bg-gray-50">
    <i :class="icon" class="text-3xl text-gray-600 mr-2"></i>
    <span class="font-medium text-gray-700">{{ name }}</span>
  </div>
</template>

<script lang="ts" setup>
defineProps({
  icon: {
    type: String,
    required: true
  },
  name: {
    type: String, 
    required: true
  }
})
</script>
