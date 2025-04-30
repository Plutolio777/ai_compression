<template>
  <div class="relative group overflow-hidden rounded-xl bg-white shadow-md hover:shadow-lg transition-all">
    <img :src="logo" :alt="company" class="w-full h-32 object-contain p-6 grayscale hover:grayscale-0 transition-all">
    <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
      <div>
        <h4 class="text-white font-bold">{{ company }}</h4>
        <p class="text-white/80 text-sm">{{ industry }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  logo: {
    type: String,
    required: true
  },
  company: {
    type: String,
    required: true
  },
  industry: {
    type: String,
    required: true
  }
})
</script>
