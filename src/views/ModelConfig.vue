<template>
  <div class="space-y-6">
    <!-- 模型选择区 -->
    <div class="bg-white p-6 rounded-lg shadow-sm">
      <h2 class="text-xl font-semibold mb-4">模型配置</h2>
      <div class="space-y-4">
        <!-- 模型选择标签页 -->
        <div class="border-b border-gray-200">
          <nav class="-mb-px flex space-x-8">
            <button 
              v-for="tab in tabs"
              :key="tab.id"
              @click="currentTab = tab.id"
              :class="[
                'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
                currentTab === tab.id 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]">
              {{ tab.name }}
            </button>
          </nav>
        </div>

        <!-- 模型配置卡 -->
        <div v-if="currentTab === 'deepseek'" class="border border-gray-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <i class="fas fa-robot text-blue-500 text-xl"></i>
              <h3 class="font-medium">DeepSeek 模型</h3>
              <span v-if="config.deepseek.isConnected" class="px-2 py-1 text-xs bg-green-100 text-green-600 rounded">已连接</span>
              <span v-else class="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">未连接</span>
            </div>
            <button @click="testConnection" class="text-blue-500 hover:text-blue-700 text-sm">
              <i class="fas fa-sync-alt mr-1"></i>刷新状态
            </button>
          </div>

          <div class="mt-4 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">API Key</label>
              <input type="password" v-model="config.deepseek.apiKey"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">API 端点</label>
              <input type="text" v-model="config.deepseek.endpoint"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500">
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">温度 (0-1.5)</label>
                <input type="number" min="0" max="1" step="0.1" v-model="config.deepseek.temperature"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500">
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">最大Token</label>
                <input type="number" min="100" max="4096" v-model="config.deepseek.maxTokens"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500">
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">子模型</label>
              <select v-model="config.deepseek.subModel"
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                <option value="deepseek-chat">deepseek-chat</option>
                <option value="deepseek-reasoner">deepseek-reasoner</option>
              </select>
            </div>
          </div>

          <div class="mt-4 flex justify-end space-x-3">
            <button @click="testConnection" 
              class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50">
              测试连接
            </button>
            <button @click="saveConfig"
              class="px-4 py-2 bg-blue-600 rounded-md shadow-sm text-sm font-medium text-white hover:bg-blue-700">
              保存配置
            </button>
          </div>
        </div>
      </div>
    </div>

        <!-- 其他模型配置卡 (预留) -->
        <div v-if="currentTab === 'openai'" class="border border-gray-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <i class="fab fa-openai text-purple-500 text-xl"></i>
              <h3 class="font-medium">OpenAI 模型</h3>
              <span class="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">未配置</span>
            </div>
          </div>
          <div class="mt-4 text-center py-8 text-gray-400">
            功能开发中，敬请期待
          </div>
        </div>

        <div v-if="currentTab === 'anthropic'" class="border border-gray-200 rounded-lg p-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <i class="fas fa-robot text-orange-500 text-xl"></i>
              <h3 class="font-medium">Anthropic 模型</h3>
              <span class="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">未配置</span>
            </div>
          </div>
          <div class="mt-4 text-center py-8 text-gray-400">
            功能开发中，敬请期待
          </div>
        </div>

        <!-- 状态监控区 -->
    <div class="bg-white p-6 rounded-lg shadow-sm">
      <h2 class="text-xl font-semibold mb-4">状态监控</h2>
      <div class="grid grid-cols-3 gap-4">
        <div class="border border-gray-200 rounded-lg p-4">
          <div class="flex items-center space-x-2">
            <span class="relative flex h-3 w-3">
              <span v-if="connectionStatus.isConnected" 
                class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-3 w-3" 
                :class="connectionStatus.isConnected ? 'bg-green-500' : 'bg-gray-500'"></span>
            </span>
            <span class="text-sm font-medium">连接状态</span>
          </div>
          <div class="mt-2 text-gray-500 text-sm">最后检测: {{connectionStatus.lastChecked || '从未检测'}}</div>
        </div>
        <div class="border border-gray-200 rounded-lg p-4">
          <div class="text-sm font-medium">响应时间</div>
          <div class="mt-1 text-2xl font-semibold">{{connectionStatus.responseTime || '--'}}ms</div>
        </div>
        <div class="border border-gray-200 rounded-lg p-4">
          <div class="text-sm font-medium">本月调用</div>
          <div class="mt-1 text-2xl font-semibold">1,248次</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import modelService from '../api/modelService'

const currentTab = ref('deepseek')
const tabs = [
  { id: 'deepseek', name: 'DeepSeek' },
  { id: 'openai', name: 'OpenAI' },
  { id: 'anthropic', name: 'Anthropic' }
]

const config = ref({
  deepseek: {
    apiKey: '',
    endpoint: '',
    temperature: 0.7,
    maxTokens: 2048,
    subModel: ''
  },
  openai: {
    apiKey: '',
    endpoint: 'https://api.openai.com/v1',
    temperature: 0.7,
    maxTokens: 2048,
    subModel: ''
  },
  anthropic: {
    apiKey: '',
    endpoint: 'https://api.anthropic.com/v1',
    temperature: 0.7,
    maxTokens: 2048,
    subModel: ''
  }
})

const connectionStatus = ref({
  isConnected: false,
  responseTime: 0,
  lastChecked: ''
})

const loadConfig = async () => {
  try {
    const res = await modelService.getConfig()
    if (res.success) {
      config.value = res.data.data
      console.log(config.value)
      // 更新连接状态
      if (res.data.deepseek?.apiKey) {
        connectionStatus.value.isConnected = true
      }
    }
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

const saveConfig = async () => {
  try {
    
    let data = {...config.value[currentTab.value]}
    data["model_type"] = currentTab.value
    const res = await modelService.saveConfig(data)
    if (res.success) {
      ElMessage.success('配置保存成功')
      // 重新加载配置
      await loadConfig()
    } else {
      ElMessage.error(`保存失败: ${res.error || '未知错误'}`)
    }
  } catch (error) {
    ElMessage.error('保存配置时发生错误')
    console.error('保存配置错误:', error)
  }
}

const testConnection = async () => {
  try {
    const res = await modelService.testConnection()
    if (res.success) {
      ElMessage.success('连接测试成功')
    } else {
      ElMessage.error(`连接失败: ${res.error || '未知错误'}`)
    }
    loadConfig()
  } catch (error) {
    ElMessage.error('测试连接时发生错误')
    console.error('测试连接错误:', error)
  }
}

// 初始化加载配置
loadConfig()
</script>
