import React from 'react'
import { Message } from './ChatInterface'
import './ChatMessages.css'

interface ChatMessagesProps {
  messages: Message[]
}

const ChatMessages: React.FC<ChatMessagesProps> = ({ messages }) => {
  return (
    <div className="chat-messages">
      {messages.length === 0 ? (
        <div className="empty-state">
          <p>メッセージを入力して添削機能をお試しください</p>
        </div>
      ) : (
        messages.map(message => (
          <div key={message.id} className={`message ${message.sender}`}>
            <div className="message-bubble">
              <p>{message.text}</p>
              <span className="timestamp">
                {message.timestamp.toLocaleTimeString('ja-JP', { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </span>
            </div>
          </div>
        ))
      )}
    </div>
  )
}

export default ChatMessages