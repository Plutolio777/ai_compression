<template>
  <div class="flex-1">
    <!-- 首屏Banner -->
    <HeroBanner />

    <div class="p-12 space-y-24">
      <!-- 核心优势 -->
      <section class="max-w-7xl mx-auto">
        <h2 class="text-3xl font-bold text-center mb-12">为什么选择我们</h2>
        <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          <StrengthCard
            icon="fas fa-bolt"
            title="极速处理"
            description="采用分布式架构，处理速度提升300%"
            iconBgColor="bg-purple-100 text-purple-600"
          />
          <StrengthCard
            icon="fas fa-shield-alt"
            title="安全可靠"
            description="企业级加密传输，数据永不泄露"
            iconBgColor="bg-green-100 text-green-600"
          />
          <StrengthCard
            icon="fas fa-cogs"
            title="智能分类"
            description="AI自动识别文档类型，准确率98%"
            iconBgColor="bg-blue-100 text-blue-600"
          />
          <StrengthCard
            icon="fas fa-infinity"
            title="多格式支持"
            description="支持100+文档格式一键转换"
            iconBgColor="bg-orange-100 text-orange-600"
          />
        </div>
      </section>

      <!-- 数据看板 -->
      <section class="max-w-7xl mx-auto">
        <h2 class="text-3xl font-bold text-center mb-12">实时数据</h2>
        <div class="grid md:grid-cols-3 gap-6">
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
      </section>

      <!-- 客户案例 -->
      <section class="max-w-7xl mx-auto">
        <h2 class="text-3xl font-bold text-center mb-12">服务客户</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
          <ClientCase 
            logo="@/assets/images/clients/alibaba.png"
            company="阿里巴巴"
            industry="互联网"
          />
          <ClientCase 
            logo="@/assets/images/clients/tencent.png"
            company="腾讯"
            industry="社交"
          />
          <ClientCase 
            logo="@/assets/images/clients/huawei.png"
            company="华为"
            industry="通信"
          />
          <ClientCase 
            logo="@/assets/images/clients/baidu.png"
            company="百度"
            industry="搜索"
          />
          <ClientCase 
            logo="@/assets/images/clients/bytedance.png"
            company="字节跳动"
            industry="内容"
          />
          <ClientCase 
            logo="@/assets/images/clients/didi.png"
            company="滴滴"
            industry="出行"
          />
        </div>
      </section>

      <!-- 合作伙伴 -->
      <section class="max-w-7xl mx-auto">
        <h2 class="text-3xl font-bold text-center mb-12">技术合作伙伴</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
          <PartnerLogo name="OpenAI" icon="fab fa-openai" />
          <PartnerLogo name="Hugging Face" icon="fas fa-robot" />
          <PartnerLogo name="阿里云" icon="iconfont icon-aliyun" />
          <PartnerLogo name="Apache" icon="fab fa-apache" />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import StatCard from '@/components/StatCard.vue';
import PartnerLogo from '@/components/PartnerLogo.vue';
import HeroBanner from '@/components/HeroBanner.vue';
import StrengthCard from '@/components/StrengthCard.vue';
import ClientCase from '@/components/ClientCase.vue';
</script>
