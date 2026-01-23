import React from 'react'

export default function ChatBox({ children }) {
  return (
    <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
      {children}
    </div>
  )
}
