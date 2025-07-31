import axios from 'axios'

export interface CorrectionVariant {
  text: string
  type: string
  reason: string
}

export interface CorrectionResponse {
  original_text: string
  variants: CorrectionVariant[]
}

export interface CorrectionRequest {
  text: string
  user_id?: string
  preferred_model?: string
  correction_style?: string  
}

export interface ModelSelectionRequest {
  user_id: string
  model_name: string
}

export interface UserSettings {
  user_id: string
  preferred_ai_model: string
  default_correction_style: string
}

export interface HistoryItem {
  id: number
  original_text: string
  corrected_text: string
  correction_type: string
  ai_model_used: string
  created_at: string
}

export interface HistoryResponse {
  total_count: number
  items: HistoryItem[]
}

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

export const correctionAPI = {
  correctText: async (request: CorrectionRequest): Promise<CorrectionResponse> => {
    const response = await api.post<CorrectionResponse>('/correct', request)
    return response.data
  },

  getAvailableModels: async (): Promise<{ models: Record<string, string> }> => {
    const response = await api.get('/models')
    return response.data
  },

  setUserModel: async (request: ModelSelectionRequest): Promise<{ message: string }> => {
    const response = await api.post('/user/model', request)
    return response.data
  },

  getUserSettings: async (userId: string): Promise<UserSettings> => {
    const response = await api.get<UserSettings>(`/user/${userId}/settings`)
    return response.data
  },

  getCorrectionHistory: async (userId: string, limit = 50, offset = 0): Promise<HistoryResponse> => {
    const response = await api.get<HistoryResponse>(`/user/${userId}/history`, {
      params: { limit, offset }
    })
    return response.data
  }
}

export default api