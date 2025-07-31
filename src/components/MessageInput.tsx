import React, { useState } from 'react'
import { Send, Edit3 } from 'lucide-react'
import CorrectionModal from './CorrectionModal'
import './MessageInput.css'

interface MessageInputProps {
  onSendMessage: (text: string) => void
}

const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage }) => {
  const [text, setText] = useState('')
  const [showCorrectionModal, setShowCorrectionModal] = useState(false)
  const [textHistory, setTextHistory] = useState<string[]>([])

  const handleSend = () => {
    if (text.trim()) {
      onSendMessage(text)
      setText('')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleCorrection = () => {
    if (text.trim()) {
      setShowCorrectionModal(true)
    }
  }

  const handleCorrectionSelect = (correctedText: string) => {
    setTextHistory(prev => [...prev, text])
    setText(correctedText)
    setShowCorrectionModal(false)
  }

  const handleUndo = () => {
    if (textHistory.length > 0) {
      const previousText = textHistory[textHistory.length - 1]
      setText(previousText)
      setTextHistory(prev => prev.slice(0, -1))
    }
  }

  return (
    <>
      <div className="message-input-container">
        <div className="input-wrapper">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="メッセージを入力..."
            className="message-textarea"
            rows={1}
          />
          <div className="input-buttons">
            {textHistory.length > 0 && (
              <button
                onClick={handleUndo}
                className="undo-button"
                title="元に戻す"
              >
                ↶
              </button>
            )}
            <button
              onClick={handleCorrection}
              className="correction-button"
              disabled={!text.trim()}
              title="添削"
            >
              <Edit3 size={18} />
              添削
            </button>
            <button
              onClick={handleSend}
              className="send-button"
              disabled={!text.trim()}
              title="送信"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>

      {showCorrectionModal && (
        <CorrectionModal
          originalText={text}
          onSelect={handleCorrectionSelect}
          onClose={() => setShowCorrectionModal(false)}
        />
      )}
    </>
  )
}

export default MessageInput