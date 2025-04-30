<template>
  <div class="flex-1 p-12 space-y-16">
    <!-- 数据看板 -->
    <div class="max-w-7xl mx-auto grid md:grid-cols-3 gap-6">
      <StatCard 
        icon="fas fa-file-archive"
        title="累计压缩文件"
        value="15.8K"
        desc="平均压缩率 78%"
        color="bg-blue-100"
      />
      <StatCard
        icon="fas fa-folder-open"
        title="文档整理效率"
        value="300%↑"
        desc="分类准确率 95%"
        color="bg-green-100"
      />
      <StatCard
        icon="fas fa-brain"
        title="AI模型调用"
        value="2.3M"
        desc="日均处理请求"
        color="bg-purple-100"
      />
    </div>

    <!-- 合作伙伴 -->
    <div class="max-w-7xl mx-auto">
      <h3 class="text-2xl font-semibold text-center mb-8">合作伙伴</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-8 opacity-75">
        <PartnerLogo name="OpenAI" icon="fab fa-openai" />
        <PartnerLogo name="Hugging Face" icon="fas fa-robot" />
        <PartnerLogo name="阿里云" icon="iconfont icon-aliyun" />
        <PartnerLogo name="Apache" icon="fab fa-apache" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import StatCard from '@/components/StatCard.vue';
import PartnerLogo from '@/components/PartnerLogo.vue';
</script>
