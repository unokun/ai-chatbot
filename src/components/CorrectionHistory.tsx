import React, { useState, useEffect } from 'react'
import { History, ChevronRight, Copy, X } from 'lucide-react'
import { correctionAPI, HistoryItem } from '../services/api'
import './CorrectionHistory.css'

interface CorrectionHistoryProps {
  userId: string
  isOpen: boolean
  onClose: () => void
}

const CorrectionHistory: React.FC<CorrectionHistoryProps> = ({ 
  userId, 
  isOpen, 
  onClose 
}) => {
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(false)
  const [totalCount, setTotalCount] = useState(0)
  const [currentPage, setCurrentPage] = useState(0)
  const itemsPerPage = 20

  useEffect(() => {
    if (isOpen) {
      loadHistory()
    }
  }, [isOpen, userId, currentPage])

  const loadHistory = async () => {
    setLoading(true)
    try {
      const response = await correctionAPI.getCorrectionHistory(
        userId, 
        itemsPerPage, 
        currentPage * itemsPerPage
      )
      
      if (currentPage === 0) {
        setHistoryItems(response.items)
      } else {
        setHistoryItems(prev => [...prev, ...response.items])
      }
      
      setTotalCount(response.total_count)
    } catch (error) {
      console.error('Failed to load history:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadMore = () => {
    if (!loading && historyItems.length < totalCount) {
      setCurrentPage(prev => prev + 1)
    }
  }

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
    } catch (error) {
      console.error('Failed to copy text:', error)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getCorrectionTypeLabel = (type: string): string => {
    switch (type) {
      case 'polite': return '丁寧な表現'
      case 'casual': return 'カジュアル表現'
      case 'corrected': return '敬語＋誤字修正'
      default: return type
    }
  }

  const getModelDisplayName = (modelName: string): string => {
    if (modelName.includes('openai')) return 'OpenAI GPT-4o'
    if (modelName.includes('claude')) return 'Claude 3'
    return modelName
  }

  if (!isOpen) return null

  return (
    <div className="correction-history-overlay" onClick={onClose}>
      <div className="correction-history-panel" onClick={(e) => e.stopPropagation()}>
        <div className="history-header">
          <div className="header-title">
            <History size={20} />
            <h3>添削履歴</h3>
            <span className="history-count">({totalCount}件)</span>
          </div>
          <button className="close-button" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="history-content">
          {historyItems.length === 0 && !loading ? (
            <div className="empty-state">
              <History size={48} />
              <p>まだ添削履歴がありません</p>
              <small>メッセージを添削すると、ここに履歴が表示されます</small>
            </div>
          ) : (
            <>
              <div className="history-list">
                {historyItems.map((item) => (
                  <div key={item.id} className="history-item">
                    <div className="item-header">
                      <span className="correction-type">
                        {getCorrectionTypeLabel(item.correction_type)}
                      </span>
                      <span className="model-used">
                        {getModelDisplayName(item.ai_model_used)}
                      </span>
                      <span className="date">
                        {formatDate(item.created_at)}
                      </span>
                    </div>
                    
                    <div className="text-comparison">
                      <div className="original-section">
                        <label>元の文章:</label>
                        <div className="text-content">
                          <p>{item.original_text}</p>
                          <button 
                            className="copy-button"
                            onClick={() => copyToClipboard(item.original_text)}
                          >
                            <Copy size={14} />
                          </button>
                        </div>
                      </div>
                      
                      <ChevronRight size={16} className="arrow" />
                      
                      <div className="corrected-section">
                        <label>添削後:</label>
                        <div className="text-content">
                          <p>{item.corrected_text}</p>
                          <button 
                            className="copy-button"
                            onClick={() => copyToClipboard(item.corrected_text)}
                          >
                            <Copy size={14} />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {historyItems.length < totalCount && (
                <div className="load-more-section">
                  <button 
                    className="load-more-button"
                    onClick={loadMore}
                    disabled={loading}
                  >
                    {loading ? 'Loading...' : 'さらに読み込む'}
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default CorrectionHistory