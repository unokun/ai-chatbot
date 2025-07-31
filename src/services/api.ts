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
}

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

export const correctionAPI = {
  correctText: async (request: CorrectionRequest): Promise<CorrectionResponse> => {
    const response = await api.post<CorrectionResponse>('/correct', request)
    return response.data
  }
}

export default api