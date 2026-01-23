import axios from 'axios'

// API基础URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// API接口
export const chatApi = {
  /**
   * 普通聊天
   */
  chat: async (data) => {
    const response = await apiClient.post('/api/chat', data)
    return response.data
  },

  /**
   * 带搜索的聊天
   */
  chatWithSearch: async (data) => {
    const response = await apiClient.post('/api/chat/search', data)
    return response.data
  },

  /**
   * 清空对话历史
   */
  clearConversation: async (sessionId) => {
    const response = await apiClient.delete(`/api/chat/${sessionId}`)
    return response.data
  },

  /**
   * 列出所有会话
   */
  listSessions: async () => {
    const response = await apiClient.get('/api/sessions')
    return response.data
  },

  /**
   * 健康检查
   */
  healthCheck: async () => {
    const response = await apiClient.get('/health')
    return response.data
  }
}

export default apiClient
