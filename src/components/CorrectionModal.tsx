import React, { useState, useEffect } from 'react'
import { X, Loader2 } from 'lucide-react'
import { correctionAPI, CorrectionVariant } from '../services/api'
import './CorrectionModal.css'

interface CorrectionModalProps {
  originalText: string
  onSelect: (correctedText: string) => void
  onClose: () => void
}

const CorrectionModal: React.FC<CorrectionModalProps> = ({
  originalText,
  onSelect,
  onClose
}) => {
  const [variants, setVariants] = useState<CorrectionVariant[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchCorrections = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const response = await correctionAPI.correctText({
          text: originalText
        })
        
        setVariants(response.variants)
      } catch (err) {
        setError('添削処理中にエラーが発生しました')
        console.error('Correction error:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchCorrections()
  }, [originalText])

  const handleVariantSelect = (variant: CorrectionVariant) => {
    onSelect(variant.text)
  }

  const getVariantLabel = (type: string): string => {
    switch (type) {
      case 'polite': return '丁寧な表現'
      case 'casual': return 'カジュアル表現'
      case 'corrected': return '敬語＋誤字修正'
      default: return type
    }
  }

  const getVariantColor = (type: string): string => {
    switch (type) {
      case 'polite': return '#2196f3'
      case 'casual': return '#ff9800'
      case 'corrected': return '#4caf50'
      default: return '#666'
    }
  }

  return (
    <div className="correction-modal-overlay" onClick={onClose}>
      <div className="correction-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>修正候補</h3>
          <button className="close-button" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-content">
          <div className="original-text">
            <label>元の文章:</label>
            <p>{originalText}</p>
          </div>

          {loading && (
            <div className="loading-state">
              <Loader2 className="spinner" size={24} />
              <p>AI が添削中...</p>
            </div>
          )}

          {error && (
            <div className="error-state">
              <p>{error}</p>
              <button onClick={onClose} className="error-button">
                閉じる
              </button>
            </div>
          )}

          {!loading && !error && variants.length > 0 && (
            <div className="variants-container">
              {variants.map((variant, index) => (
                <div
                  key={index}
                  className="variant-item"
                  onClick={() => handleVariantSelect(variant)}
                >
                  <div className="variant-header">
                    <span 
                      className="variant-label"
                      style={{ color: getVariantColor(variant.type) }}
                    >
                      {String.fromCharCode(65 + index)}: {getVariantLabel(variant.type)}
                    </span>
                  </div>
                  <div className="variant-text">
                    {variant.text}
                  </div>
                  <div className="variant-reason">
                    → {variant.reason}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button onClick={onClose} className="cancel-button">
            キャンセル
          </button>
        </div>
      </div>
    </div>
  )
}

export default CorrectionModal