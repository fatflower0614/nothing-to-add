import React, { useState } from 'react'
import PropTypes from 'prop-types'

export default function InputArea({ onSendMessage, disabled }) {
  const [input, setInput] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (input.trim() && !disabled) {
      onSendMessage(input)
      setInput('')
    }
  }

  return (
    <div className="border-t border-gray-200 p-4">
      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="向巴菲特和芒格提问..."
          disabled={disabled}
          className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
        />

        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
        >
          {disabled ? '思考中...' : '发送'}
        </button>
      </form>

      {/* 快捷问题 */}
      <div className="mt-3 flex flex-wrap gap-2">
        <QuickQuestion
          text="什么是价值投资？"
          onClick={() => setInput('什么是价值投资？')}
          disabled={disabled}
        />
        <QuickQuestion
          text="如何寻找有护城河的企业？"
          onClick={() => setInput('如何寻找有护城河的企业？')}
          disabled={disabled}
        />
        <QuickQuestion
          text="给我一些人生建议"
          onClick={() => setInput('给我一些人生建议')}
          disabled={disabled}
        />
        <QuickQuestion
          text="如何看待当前的市场？"
          onClick={() => setInput('如何看待当前的市场？')}
          disabled={disabled}
        />
      </div>
    </div>
  )
}

InputArea.propTypes = {
  onSendMessage: PropTypes.func.isRequired,
  disabled: PropTypes.bool
}

function QuickQuestion({ text, onClick, disabled }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
    >
      {text}
    </button>
  )
}

QuickQuestion.propTypes = {
  text: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
  disabled: PropTypes.bool
}
