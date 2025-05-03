import apiService from './apiService';

export default {
  /**
   * 获取模型配置
   * @returns {Promise<{success: boolean, data?: Object, error?: string}>}
   */
  async getConfig() {
    return await apiService.getModelConfig();
  },

  /**
   * 保存模型配置
   * @param {Object} config - 模型配置对象
   * @returns {Promise<{success: boolean, error?: string}>}
   */
  async saveConfig(config) {
    return await apiService.saveModelConfig({...config});
  },

  /**
   * 测试模型连接
   * @returns {Promise<{success: boolean, is_connected?: boolean, response_time?: number, error?: string}>}
   */
  async testConnection() {
    return await apiService.testModelConnection({
      model_type: 'deepseek'
    });
  },

  /**
   * 测试模型调用
   * @param {string} prompt - 输入的提示词
   * @returns {Promise<{success: boolean, response?: string, error?: string}>}
   */
  async testModel(prompt) {
    return await apiService.testModel({
      prompt
    });
  }
};
