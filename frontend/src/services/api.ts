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

// ==========================================
// DONATION INTERFACES
// ==========================================

interface VoluntaryDonation {
  id: number
  donor: number | null
  donor_name: string
  donor_email: string | null
  amount: number
  message: string
  is_anonymous: boolean
  payment_proof: string | null
  donated_at: string
  verified_by: number | null
  verified_by_name: string
  verified_at: string | null
  display_name: string
  is_verified: boolean
}

interface VoluntaryDonationCreate {
  amount: number
  message?: string
  is_anonymous?: boolean
  payment_proof?: File
}

interface DonationRequest {
  id: number
  requested_by: number
  requester_name: string
  requester_email: string
  recipient_name: string
  recipient_description: string
  amount: number
  reason: string
  urgency_level: 'low' | 'medium' | 'high' | 'critical'
  urgency_display: string
  status: 'pending_approval' | 'approved' | 'rejected'
  status_display: string
  reviewed_by: number | null
  reviewed_by_name: string
  rejection_reason: string
  created_at: string
  approved_at: string | null
  updated_at: string
  can_edit: boolean
  can_delete: boolean
}

interface DonationRequestCreate {
  recipient_name: string
  recipient_description: string
  amount: number
  reason: string
  urgency_level: 'low' | 'medium' | 'high' | 'critical'
}

interface MembershipFee {
  id: number
  user: number
  user_email: string
  user_name: string
  competency_month: string
  amount: number
  due_date: string
  status: 'pending' | 'paid' | 'overdue'
  paid_at: string | null
  is_overdue: boolean
  days_overdue: number
  created_at: string
}

class ApiService {
  private getAuthToken(): string | null {
    return localStorage.getItem('auth_token')
  }

  private async request<T = any>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      console.log('API Request:', `${API_BASE_URL}${endpoint}`, options)

      const headers: HeadersInit = {
        ...options.headers,
      }

      // Add auth token if available
      const token = this.getAuthToken()
      if (token) {
        headers['Authorization'] = `Token ${token}`
      }

      // Only add Content-Type for non-FormData requests
      if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json'
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers,
        ...options,
      })

      const contentType = response.headers.get('content-type')
      console.log('Response Content-Type:', contentType)
      console.log('Response Status:', response.status)

      // Handle 204 No Content (DELETE success)
      if (response.status === 204) {
        return {
          data: null,
          error: undefined,
          status: 204,
        }
      }

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

      // Handle 401 Unauthorized - token expired/invalid
      if (response.status === 401) {
        // Clear auth data
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user')

        // Redirect to login (only if not already on login page)
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login?expired=true'
        }
      }

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

  // ==========================================
  // ONBOARDING
  // ==========================================

  async submitOnboarding(data: OnboardingData): Promise<ApiResponse> {
    return this.request('/users/onboarding/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // ==========================================
  // MEMBERSHIP FEES
  // ==========================================

  async getMyFees(): Promise<ApiResponse<MembershipFee[]>> {
    return this.request('/finance/fees/my_fees/')
  }

  async getAllFees(): Promise<ApiResponse<MembershipFee[]>> {
    return this.request('/finance/fees/')
  }

  // ==========================================
  // VOLUNTARY DONATIONS (TO ORBE)
  // ==========================================

  async createVoluntaryDonation(data: VoluntaryDonationCreate): Promise<ApiResponse<VoluntaryDonation>> {
    const formData = new FormData()
    formData.append('amount', data.amount.toString())
    if (data.message) formData.append('message', data.message)
    if (data.is_anonymous !== undefined) formData.append('is_anonymous', data.is_anonymous.toString())
    if (data.payment_proof) formData.append('payment_proof', data.payment_proof)

    return this.request('/finance/voluntary-donations/', {
      method: 'POST',
      body: formData,
    })
  }

  async getMyVoluntaryDonations(): Promise<ApiResponse<VoluntaryDonation[]>> {
    return this.request('/finance/voluntary-donations/my_donations/')
  }

  async getAllVoluntaryDonations(): Promise<ApiResponse<VoluntaryDonation[]>> {
    return this.request('/finance/voluntary-donations/')
  }

  async getPendingVoluntaryDonations(): Promise<ApiResponse<VoluntaryDonation[]>> {
    return this.request('/finance/voluntary-donations/pending_verification/')
  }

  async verifyVoluntaryDonation(id: number): Promise<ApiResponse<VoluntaryDonation>> {
    return this.request(`/finance/voluntary-donations/${id}/verify/`, {
      method: 'POST',
    })
  }

  // ==========================================
  // DONATION REQUESTS (FOR THIRD PARTIES)
  // ==========================================

  async createDonationRequest(data: DonationRequestCreate): Promise<ApiResponse<DonationRequest>> {
    return this.request('/finance/donation-requests/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getMyDonationRequests(): Promise<ApiResponse<DonationRequest[]>> {
    return this.request('/finance/donation-requests/my_requests/')
  }

  async getAllDonationRequests(): Promise<ApiResponse<DonationRequest[]>> {
    return this.request('/finance/donation-requests/')
  }

  async getPendingDonationRequests(): Promise<ApiResponse<DonationRequest[]>> {
    return this.request('/finance/donation-requests/pending_approval/')
  }

  async approveDonationRequest(id: number): Promise<ApiResponse<DonationRequest>> {
    return this.request(`/finance/donation-requests/${id}/approve/`, {
      method: 'POST',
    })
  }

  async rejectDonationRequest(id: number, reason: string): Promise<ApiResponse<DonationRequest>> {
    return this.request(`/finance/donation-requests/${id}/reject/`, {
      method: 'POST',
      body: JSON.stringify({ rejection_reason: reason }),
    })
  }

  async getDonationRequestStats(): Promise<ApiResponse<any>> {
    return this.request('/finance/donation-requests/stats/')
  }

  async updateDonationRequest(id: number, data: Partial<DonationRequestCreate>): Promise<ApiResponse<DonationRequest>> {
    return this.request(`/finance/donation-requests/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async deleteDonationRequest(id: number): Promise<ApiResponse<void>> {
    return this.request(`/finance/donation-requests/${id}/`, {
      method: 'DELETE',
    })
  }

  // ==========================================
  // ASSISTANCE CASES
  // ==========================================

  async getAssistanceCases(): Promise<ApiResponse<any[]>> {
    return this.request('/assistance/cases/')
  }

  async getAssistanceCase(id: number): Promise<ApiResponse<any>> {
    return this.request(`/assistance/cases/${id}/`)
  }

  async submitBankInfo(caseId: number, bankData: any): Promise<ApiResponse<any>> {
    return this.request(`/assistance/cases/${caseId}/submit_bank_info/`, {
      method: 'POST',
      body: JSON.stringify(bankData),
    })
  }

  async confirmTransfer(caseId: number): Promise<ApiResponse<any>> {
    return this.request(`/assistance/cases/${caseId}/confirm_transfer/`, {
      method: 'POST',
    })
  }

  async submitMemberProof(caseId: number): Promise<ApiResponse<any>> {
    return this.request(`/assistance/cases/${caseId}/submit_member_proof/`, {
      method: 'POST',
    })
  }

  async completeCase(caseId: number): Promise<ApiResponse<any>> {
    return this.request(`/assistance/cases/${caseId}/complete/`, {
      method: 'POST',
    })
  }

  async uploadAttachment(formData: FormData): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/assistance/attachments/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${this.getAuthToken()}`,
        },
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        // Return error in ApiResponse format
        return {
          error: data.detail || data.error || data.message || 'Erro ao fazer upload do arquivo',
          data: null
        }
      }

      return { data, error: null }
    } catch (err: any) {
      return {
        error: err.message || 'Erro de conexão ao fazer upload',
        data: null
      }
    }
  }

  async deleteAttachment(attachmentId: number): Promise<ApiResponse<any>> {
    return this.request(`/assistance/attachments/${attachmentId}/`, {
      method: 'DELETE',
    })
  }
}

export const apiService = new ApiService()
export const api = apiService // Export as 'api' for convenience

export type {
  OnboardingData,
  VoluntaryDonation,
  VoluntaryDonationCreate,
  DonationRequest,
  DonationRequestCreate,
  MembershipFee
}