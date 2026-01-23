import { useState, useEffect, useRef } from 'react'
import ChatBox from './components/ChatBox'
import MessageList from './components/MessageList'
import InputArea from './components/InputArea'
import { chatApi } from './api/client'

function App() {
  const [messages, setMessages] = useState([])
  const [sessionId, setSessionId] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [useSearch, setUseSearch] = useState(false)
  const messagesEndRef = useRef(null)

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 发送消息
  const handleSendMessage = async (message) => {
    if (!message.trim() || isLoading) return

    // 添加用户消息
    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      // 调用API
      const apiFunction = useSearch ? chatApi.chatWithSearch : chatApi.chat
      const response = await apiFunction({
        message: message,
        session_id: sessionId,
        use_search: useSearch
      })

      // 添加AI回复
      const aiMessage = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        usedSearch: response.used_search || false,
        timestamp: new Date().toISOString()
      }

      setMessages(prev => [...prev, aiMessage])

      // 更新session ID
      if (response.session_id) {
        setSessionId(response.session_id)
      }

    } catch (error) {
      console.error('Error sending message:', error)

      // 添加错误消息
      const errorMessage = {
        role: 'assistant',
        content: '抱歉，我遇到了一些问题。请稍后再试。',
        isError: true,
        timestamp: new Date().toISOString()
      }

      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  // 清空对话
  const handleClearConversation = async () => {
    try {
      if (sessionId) {
        await chatApi.clearConversation(sessionId)
      }

      setMessages([])
      setSessionId(null)

    } catch (error) {
      console.error('Error clearing conversation:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-yellow-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">
                Nothing to Add
              </h1>
              <p className="text-sm text-gray-600">
                巴菲特与芒格AI Agent - 投资智慧的传承
              </p>
            </div>

            <div className="flex items-center gap-4">
              {/* 搜索开关 */}
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={useSearch}
                  onChange={(e) => setUseSearch(e.target.checked)}
                  className="w-4 h-4 text-orange-600 rounded focus:ring-orange-500"
                />
                <span className="text-gray-700">联网搜索</span>
              </label>

              {/* 清空按钮 */}
              <button
                onClick={handleClearConversation}
                className="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                新对话
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-6">
        <ChatBox>
          <MessageList
            messages={messages}
            isLoading={isLoading}
          />

          <div ref={messagesEndRef} />

          <InputArea
            onSendMessage={handleSendMessage}
            disabled={isLoading}
          />
        </ChatBox>
      </main>

      {/* Footer */}
      <footer className="max-w-4xl mx-auto px-4 py-4 text-center text-sm text-gray-500">
        <p>
          Nothing to Add, Except Wisdom - 传承巴菲特与芒格的投资智慧
        </p>
        <p className="mt-1 text-xs">
          本AI Agent仅供教育和学习目的，不构成投资建议
        </p>
      </footer>
    </div>
  )
}

export default App
