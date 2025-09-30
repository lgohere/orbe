/**
 * API service for ORBE platform
 */

const API_BASE_URL = '/api'

interface OnboardingData {
  first_name: string
  last_name: string
  email: string
  phone: string
  city: string
  state: string
  country: string
  membership_due_day: number
  theme_preference: string
  language_preference: string
  terms_accepted: boolean
  privacy_accepted: boolean
}

interface ApiResponse<T = any> {
  data?: T
  error?: string
  status: number
}

class ApiService {
  private async request<T = any>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      console.log('API Request:', `${API_BASE_URL}${endpoint}`, options)

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      })

      const contentType = response.headers.get('content-type')
      console.log('Response Content-Type:', contentType)
      console.log('Response Status:', response.status)

      let data
      if (contentType && contentType.includes('application/json')) {
        data = await response.json()
      } else {
        // Server returned HTML (error page), get the text
        const text = await response.text()
        console.error('Server returned HTML instead of JSON:', text)
        return {
          error: `Server error (${response.status}): Check Django server logs`,
          status: response.status,
        }
      }

      console.log('API Response:', { status: response.status, data })

      return {
        data: response.ok ? data : undefined,
        error: !response.ok ? (data.detail || data.message || data.error || JSON.stringify(data)) : undefined,
        status: response.status,
      }
    } catch (error) {
      console.error('API Error:', error)
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      }
    }
  }

  async submitOnboarding(data: OnboardingData): Promise<ApiResponse> {
    return this.request('/users/onboarding/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }
}

export const apiService = new ApiService()
export type { OnboardingData }