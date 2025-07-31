import React, { useState } from 'react'
import MessageInput from './MessageInput'
import ChatMessages from './ChatMessages'
import './ChatInterface.css'

export interface Message {
  id: string
  text: string
  timestamp: Date
  sender: 'user' | 'system'
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([])

  const handleSendMessage = (text: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      timestamp: new Date(),
      sender: 'user'
    }
    setMessages(prev => [...prev, newMessage])
  }

  return (
    <div className="chat-interface">
      <div className="chat-container">
        <ChatMessages messages={messages} />
        <MessageInput onSendMessage={handleSendMessage} />
      </div>
    </div>
  )
}

export default ChatInterface