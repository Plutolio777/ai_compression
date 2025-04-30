<template>
  <div class="relative h-screen max-h-[800px] overflow-hidden">
    <!-- 背景图片 -->
    <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-blue-900 to-blue-600">
      <img src="https://src.fanruan.com/2023-website/2023-finebi/img/FineBI8.png" alt="AI文档处理" class="w-full h-full object-cover">
    </div>
    
    <!-- 内容层 -->
    <div class="relative z-10 h-full flex flex-col justify-center px-36 text-white">
      <div class="max-w-4xl space-y-8 text-left">
        <h1 class="text-5xl md:text-6xl font-bold leading-tight text-black">
          智能文档压缩管理平台
        </h1>
        <p class="text-xl md:text-2xl max-w-2xl text-black">
          企业级AI文档处理解决方案，提升效率300%
        </p>
        <div class="flex flex-col sm:flex-row gap-4 pt-4">
          <button class="px-8 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-lg font-medium transition-all">
            免费试用
          </button>
          <button class="px-8 py-3 bg-white text-gray-900 hover:bg-gray-100 rounded-lg text-lg font-medium transition-all">
            产品演示
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 视频背景需要准备hero-bg.mp4放到assets/videos目录
</script>
