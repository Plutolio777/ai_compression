<template>
  <div class="space-y-4">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <el-form-item label="文件大小范围">
        <el-select 
          v-model="modelValue.sizeRange" 
          class="w-full"
          @change="handleSizeRangeChange"
        >
          <el-option label="小文件 (<1MB)" value="small" />
          <el-option label="中等文件 (1MB-10MB)" value="medium" />
          <el-option label="大文件 (>10MB)" value="large" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="推荐算法">
        <el-select 
          v-model="modelValue.algorithm" 
          class="w-full"
          placeholder="根据文件大小自动推荐"
        >
          <el-option label="ZIP" value="zip" />
          <el-option label="GZIP" value="gzip" />
          <el-option label="BZ2" value="bz2" />
          <el-option label="LZMA" value="lzma" />
        </el-select>
      </el-form-item>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <el-form-item label="分卷压缩">
        <el-switch
          v-model="modelValue.splitVolume"
          active-text="启用"
          inactive-text="禁用"
        />
      </el-form-item>

      <div v-if="modelValue.splitVolume">
        <el-form-item label="分卷大小(MB)">
          <el-input-number 
            v-model="modelValue.volumeSize" 
            :min="1" 
            :max="1000"
            controls-position="right"
            class="w-full"
          />
        </el-form-item>
      </div>
    </div>
  </div>
</template>

<script setup>
import { watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
})

const handleSizeRangeChange = (val) => {
  // 根据文件大小自动推荐算法
  switch(val) {
    case 'small':
      props.rule.algorithm = 'zip' // 小文件用ZIP快速压缩
      break
    case 'medium':
      props.rule.algorithm = 'gzip' // 中等文件用GZIP平衡压缩
      break
    case 'large':
      props.rule.algorithm = 'lzma' // 大文件用LZMA高压缩率
      break
  }
}
</script>
