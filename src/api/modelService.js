import apiService from './apiService'

// 开发环境模拟延迟（1-3秒随机）
const simulateDelay = () => new Promise(resolve => 
  setTimeout(resolve, 1000 + Math.random() * 2000)
)

const mockConfig = {
  deepseek: {
    apiKey: 'dev_xxxxxx',
    endpoint: 'https://api.deepseek.com/v1/chat',
    temperature: 0.7,
    maxTokens: 2048,
    status: 'connected'
  }
}

export default {
  async getConfig() {
    if (import.meta.env.MODE === 'development') {
      await simulateDelay()
      return { success: true, data: mockConfig }
    }
    return apiService.getModelConfig()
  },

  async saveConfig(config) {
    if (import.meta.env.MODE === 'development') {
      await simulateDelay()
      Object.assign(mockConfig.deepseek, config)
      return { success: true }
    }
    return apiService.saveModelConfig(config)
  },

  async testConnection() {
    if (import.meta.env.MODE === 'development') {
      await simulateDelay()
      return { 
        success: Math.random() > 0.2,
        latency: 300 + Math.random() * 700,
        message: Math.random() > 0.2 ? '连接成功' : '连接超时'
      }
    }
    return apiService.testModelConnection()
  }
}
