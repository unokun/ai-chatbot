import React, { useState, useEffect } from 'react'
import { Settings, ChevronDown, Check } from 'lucide-react'
import { correctionAPI } from '../services/api'
import './ModelSelector.css'

interface ModelSelectorProps {
  userId: string
  onModelChange?: (modelName: string) => void
}

const ModelSelector: React.FC<ModelSelectorProps> = ({ userId, onModelChange }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [availableModels, setAvailableModels] = useState<Record<string, string>>({})
  const [selectedModel, setSelectedModel] = useState<string>('openai-gpt4o')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const loadModelsAndSettings = async () => {
      try {
        // Load available models
        const modelsResponse = await correctionAPI.getAvailableModels()
        setAvailableModels(modelsResponse.models)

        // Load user settings
        const userSettings = await correctionAPI.getUserSettings(userId)
        setSelectedModel(userSettings.preferred_ai_model)
      } catch (error) {
        console.error('Failed to load models or settings:', error)
      }
    }

    loadModelsAndSettings()
  }, [userId])

  const handleModelSelect = async (modelName: string) => {
    if (modelName === selectedModel) {
      setIsOpen(false)
      return
    }

    setLoading(true)
    try {
      await correctionAPI.setUserModel({
        user_id: userId,
        model_name: modelName
      })
      
      setSelectedModel(modelName)
      setIsOpen(false)
      
      if (onModelChange) {
        onModelChange(modelName)
      }
    } catch (error) {
      console.error('Failed to update model preference:', error)
    } finally {
      setLoading(false)
    }
  }

  const getModelDisplayName = (modelName: string): string => {
    return availableModels[modelName] || modelName
  }

  const getModelBadge = (modelName: string): string => {
    if (modelName.includes('openai')) return 'OpenAI'
    if (modelName.includes('claude')) return 'Claude'
    return 'AI'
  }

  return (
    <div className="model-selector">
      <button 
        className="model-selector-trigger"
        onClick={() => setIsOpen(!isOpen)}
        disabled={loading}
      >
        <Settings size={16} />
        <span className="model-name">
          {getModelDisplayName(selectedModel)}
        </span>
        <span className="model-badge">
          {getModelBadge(selectedModel)}
        </span>
        <ChevronDown size={16} className={`chevron ${isOpen ? 'open' : ''}`} />
      </button>

      {isOpen && (
        <div className="model-dropdown">
          <div className="dropdown-header">
            <h4>AIモデル選択</h4>
          </div>
          <div className="model-list">
            {Object.entries(availableModels).map(([modelName, displayName]) => (
              <button
                key={modelName}
                className={`model-option ${selectedModel === modelName ? 'selected' : ''}`}
                onClick={() => handleModelSelect(modelName)}
                disabled={loading}
              >
                <div className="model-info">
                  <span className="model-display-name">{displayName}</span>
                  <span className="model-provider">{getModelBadge(modelName)}</span>
                </div>
                {selectedModel === modelName && <Check size={16} />}
              </button>
            ))}
          </div>
          <div className="dropdown-footer">
            <small>選択したモデルが次回の添削から適用されます</small>
          </div>
        </div>
      )}
    </div>
  )
}

export default ModelSelector