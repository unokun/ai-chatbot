import React, { useState } from 'react'
import { ChevronDown, Settings } from 'lucide-react'
import './CorrectionStyleSelector.css'

export interface CorrectionStyle {
  id: string
  name: string
  description: string
  icon?: string
}

interface CorrectionStyleSelectorProps {
  selectedStyle: string
  onStyleChange: (styleId: string) => void
  disabled?: boolean
}

const CORRECTION_STYLES: CorrectionStyle[] = [
  {
    id: 'default',
    name: '標準',
    description: 'バランスの良い一般的な添削'
  },
  {
    id: 'formal',
    name: '丁寧',
    description: '敬語を重視したフォーマルな表現'
  },
  {
    id: 'casual',
    name: 'カジュアル',
    description: '親しみやすい自然な表現'
  },
  {
    id: 'business',
    name: 'ビジネス',
    description: '商談・会議に適した表現'
  },
  {
    id: 'error_focus',
    name: '誤字重視',
    description: '誤字脱字の修正を優先'
  },
  {
    id: 'concise',
    name: '簡潔',
    description: '冗長な表現を削り簡潔に'
  }
]

const CorrectionStyleSelector: React.FC<CorrectionStyleSelectorProps> = ({
  selectedStyle,
  onStyleChange,
  disabled = false
}) => {
  const [isOpen, setIsOpen] = useState(false)
  
  const selectedStyleObj = CORRECTION_STYLES.find(s => s.id === selectedStyle) || CORRECTION_STYLES[0]
  
  const handleStyleSelect = (styleId: string) => {
    onStyleChange(styleId)
    setIsOpen(false)
  }
  
  const handleToggle = () => {
    if (!disabled) {
      setIsOpen(!isOpen)
    }
  }
  
  return (
    <div className={`correction-style-selector ${isOpen ? 'open' : ''} ${disabled ? 'disabled' : ''}`}>
      <button 
        className="style-selector-button"
        onClick={handleToggle}
        disabled={disabled}
        aria-label="添削スタイルを選択"
      >
        <Settings size={14} />
        <span className="selected-style-name">{selectedStyleObj.name}</span>
        <ChevronDown size={14} className={`chevron ${isOpen ? 'rotated' : ''}`} />
      </button>
      
      {isOpen && (
        <div className="style-dropdown">
          <div className="dropdown-header">
            <span>添削スタイル</span>
          </div>
          <div className="style-options">
            {CORRECTION_STYLES.map((style) => (
              <button
                key={style.id}
                className={`style-option ${selectedStyle === style.id ? 'selected' : ''}`}
                onClick={() => handleStyleSelect(style.id)}
              >
                <div className="style-option-content">
                  <span className="style-name">{style.name}</span>
                  <span className="style-description">{style.description}</span>
                </div>
                {selectedStyle === style.id && (
                  <div className="selection-indicator">✓</div>
                )}
              </button>
            ))}
          </div>
        </div>
      )}
      
      {isOpen && (
        <div 
          className="style-selector-overlay"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  )
}

export default CorrectionStyleSelector