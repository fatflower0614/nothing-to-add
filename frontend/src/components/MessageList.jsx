import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'

export default function MessageList({ messages, isLoading }) {
  return (
    <div className="h-[600px] overflow-y-auto p-6 space-y-6">
      {/* 欢迎消息 */}
      {messages.length === 0 && (
        <div className="text-center py-12">
          <div className="mb-8 flex justify-center gap-8">
            {/* 巴菲特头像 - 带动画 */}
            <div className="text-center">
              <div className="relative w-40 h-40 mx-auto mb-3">
                {/* 头像 */}
                <div className="w-full h-full rounded-full bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center text-white text-6xl font-bold shadow-2xl animate-float">
                  巴
                </div>

                {/* 嘴巴动画（暗示状态） */}
                <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2">
                  <div className="w-8 h-4 bg-white rounded-full opacity-0"></div>
                </div>
              </div>
              <p className="text-sm font-medium text-gray-700">沃伦·巴菲特</p>
              <p className="text-xs text-gray-500">Warren Buffett</p>
              <p className="text-xs text-orange-600 mt-1">🏆 奥马哈的先知</p>
            </div>

            {/* 芒格头像 - 带动画 */}
            <div className="text-center">
              <div className="relative w-40 h-40 mx-auto mb-3">
                {/* 头像 */}
                <div className="w-full h-full rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-6xl font-bold shadow-2xl animate-float" style={{ animationDelay: '1s' }}>
                  芒
                </div>

                {/* 嘴巴动画（暗示状态） */}
                <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2">
                  <div className="w-8 h-4 bg-white rounded-full opacity-0"></div>
                </div>
              </div>
              <p className="text-sm font-medium text-gray-700">查理·芒格</p>
              <p className="text-xs text-gray-500">Charlie Munger</p>
              <p className="text-xs text-blue-600 mt-1">💡 多学科思维者</p>
            </div>
          </div>

          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Nothing to Add, Except Wisdom
          </h2>
          <p className="text-gray-600 mb-6">
            向巴菲特和芒格提问任何关于投资、人生或商业的问题
          </p>

          <div className="grid grid-cols-2 gap-4 max-w-md mx-auto text-sm">
            <div className="p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors cursor-pointer">
              <p className="font-medium text-orange-800 mb-1">💼 公司分析</p>
              <p className="text-orange-600 text-xs">评估企业价值与护城河</p>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors cursor-pointer">
              <p className="font-medium text-blue-800 mb-1">💡 人生智慧</p>
              <p className="text-blue-600 text-xs">获取生活与决策建议</p>
            </div>
          </div>
        </div>
      )}

      {/* 消息列表 */}
      {messages.map((message, index) => (
        <MessageItem
          key={index}
          message={message}
        />
      ))}

      {/* 加载中 - 带嘴巴动画 */}
      {isLoading && (
        <div className="flex items-start gap-3">
          <div className="relative">
            <SpeakingAvatar name="巴菲特" color="orange" isSpeaking={true} />
          </div>
          <div className="flex-1">
            <div className="inline-block px-4 py-2 bg-gray-100 rounded-lg">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></span>
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

MessageList.propTypes = {
  messages: PropTypes.array.isRequired,
  isLoading: PropTypes.bool
}

function MessageItem({ message }) {
  const [isSpeaking, setIsSpeaking] = useState(false)

  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="flex items-start gap-3 justify-end">
        <div className="max-w-[80%]">
          <div className="inline-block px-4 py-2 bg-orange-500 text-white rounded-lg">
            {message.content}
          </div>
          <p className="text-xs text-gray-500 mt-1 text-right">
            {new Date(message.timestamp).toLocaleTimeString()}
          </p>
        </div>
        <div className="w-10 h-10 rounded-full bg-gray-300 flex items-center justify-center text-gray-600 font-bold flex-shrink-0">
          你
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-start gap-3">
      <SpeakingAvatar name="AI" color="orange" isSpeaking={isSpeaking} />

      <div className="flex-1">
        <div className="inline-block px-4 py-2 bg-gray-100 rounded-lg max-w-[80%]">
          <p className="text-gray-800 whitespace-pre-wrap">{message.content}</p>

          {/* 来源 */}
          {message.sources && message.sources.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <p className="text-xs text-gray-500 mb-1">📚 来源：</p>
              {message.sources.slice(0, 2).map((source, idx) => (
                <p key={idx} className="text-xs text-gray-400">
                  {source.metadata?.source || '未知来源'}
                  {source.metadata?.year && ` (${source.metadata?.year})`}
                </p>
              ))}
            </div>
          )}

          {/* 搜索标识 */}
          {message.usedSearch && (
            <div className="mt-2 flex items-center gap-1 text-xs text-blue-600">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span>使用了联网搜索</span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2 mt-2">
          <p className="text-xs text-gray-500">
            {new Date(message.timestamp).toLocaleTimeString()}
          </p>

          {/* 语音播放按钮 */}
          <button
            onClick={() => {
              speak(message.content, setIsSpeaking)
            }}
            className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
            </svg>
            {isSpeaking ? '播放中...' : '播放'}
          </button>
        </div>
      </div>
    </div>
  )
}

MessageItem.propTypes = {
  message: PropTypes.object.isRequired
}

// 说话的头像组件（带嘴巴动画）
function SpeakingAvatar({ name, color, isSpeaking }) {
  const colorClasses = {
    orange: 'from-orange-400 to-orange-600',
    blue: 'from-blue-400 to-blue-600'
  }

  return (
    <div className="relative w-10 h-10 flex-shrink-0">
      <div className={`w-full h-full rounded-full bg-gradient-to-br ${colorClasses[color]} flex items-center justify-center text-white font-bold`}>
        {name === 'AI' ? 'AI' : name[0]}
      </div>

      {/* 嘴巴动画 */}
      {isSpeaking && (
        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2">
          <div className="w-6 h-3 bg-white rounded-full animate-mouth"></div>
        </div>
      )}
    </div>
  )
}

// 语音播放函数
function speak(text, setIsSpeaking) {
  if ('speechSynthesis' in window) {
    // 停止当前播放
    window.speechSynthesis.cancel()

    // 创建新的语音
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'zh-CN'
    utterance.rate = 0.9  // 稍慢一点，更像老人说话
    utterance.pitch = 0.9  // 稍低沉一点

    utterance.onstart = () => setIsSpeaking(true)
    utterance.onend = () => setIsSpeaking(false)
    utterance.onerror = () => setIsSpeaking(false)

    window.speechSynthesis.speak(utterance)
  } else {
    alert('您的浏览器不支持语音播放')
  }
}
