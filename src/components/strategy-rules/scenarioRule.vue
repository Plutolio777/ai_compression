<template>
  <div class="space-y-4">
    <el-form-item label="业务场景">
      <el-select v-model="modelValue.scenario" class="w-full">
        <el-option label="存储优化" value="storage" />
        <el-option label="传输加速" value="transfer" />
        <el-option label="备份归档" value="backup" />
        <el-option label="生产环境" value="production" />
      </el-select>
    </el-form-item>

    <div v-if="modelValue.scenario === 'storage'">
      <el-form-item label="存储优化选项">
        <el-checkbox-group v-model="modelValue.options">
          <el-checkbox label="deduplication">去重</el-checkbox>
          <el-checkbox label="compression">压缩</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  rule: {
    type: Object,
    required: true
  }
})
</script>
