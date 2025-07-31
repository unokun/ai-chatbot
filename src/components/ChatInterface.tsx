import React, { useState } from 'react'
import { History } from 'lucide-react'
import MessageInput from './MessageInput'
import ChatMessages from './ChatMessages'
import ModelSelector from './ModelSelector'
import CorrectionHistory from './CorrectionHistory'
import './ChatInterface.css'

export interface Message {
  id: string
  text: string
  timestamp: Date
  sender: 'user' | 'system'
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [selectedModel, setSelectedModel] = useState<string>('openai-gpt4o')
  const [historyOpen, setHistoryOpen] = useState(false)
  
  // Generate a simple user ID for demo purposes
  const userId = 'demo-user'

  const handleSendMessage = (text: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      timestamp: new Date(),
      sender: 'user'
    }
    setMessages(prev => [...prev, newMessage])
  }

  const handleModelChange = (modelName: string) => {
    setSelectedModel(modelName)
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <div className="header-left">
          <h2>AI添削チャット</h2>
        </div>
        <div className="header-right">
          <ModelSelector 
            userId={userId} 
            onModelChange={handleModelChange}
          />
          <button 
            className="history-button"
            onClick={() => setHistoryOpen(true)}
          >
            <History size={16} />
            履歴
          </button>
        </div>
      </div>
      
      <div className="chat-container">
        <ChatMessages messages={messages} />
        <MessageInput 
          onSendMessage={handleSendMessage} 
          userId={userId}
          preferredModel={selectedModel}
        />
      </div>
      
      <CorrectionHistory
        userId={userId}
        isOpen={historyOpen}
        onClose={() => setHistoryOpen(false)}
      />
    </div>
  )
}

export default ChatInterface