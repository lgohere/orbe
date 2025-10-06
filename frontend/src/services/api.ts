/**
 * Central API service for the ORBE platform.
 * Provides a single integration point between the Vue frontend and the Django backend,
 * keeping the modular monolith well-organised and environment agnostic.
 */

const DEFAULT_API_PATH = '/api'

function guessApiBase(): string {
  if (typeof window === 'undefined') {
    return DEFAULT_API_PATH
  }

  const { protocol, hostname, port } = window.location
  const portMap: Record<string, string> = {
    '3000': '8000',
    '3001': '8001',
    '5173': '8000',
  }

  const inferredPort = port ? portMap[port] : undefined

  if (inferredPort) {
    return `${protocol}//${hostname}:${inferredPort}${DEFAULT_API_PATH}`
  }

  const normalizedPort = port ? `:${port}` : ''
  return `${protocol}//${hostname}${normalizedPort}${DEFAULT_API_PATH}`
}

const rawBaseUrl = (import.meta.env.VITE_API_URL as string | undefined)?.trim()
const baseCandidate = rawBaseUrl && rawBaseUrl.length > 0 ? rawBaseUrl : guessApiBase()
const normalizedBase = baseCandidate.replace(/\/$/, '')

export const API_BASE_URL = normalizedBase

export interface ApiResponse<T = any> {
  data?: T
  error?: string
  status: number
}

export interface OnboardingData {
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

export interface UserProfile {
  phone: string
  city: string
  state: string
  country: string
  membership_due_day: number
  theme_preference: 'white' | 'black'
  language_preference: 'pt-BR' | 'en' | 'es'
  is_onboarding_completed: boolean
}

export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  role: 'SUPER_ADMIN' | 'BOARD' | 'FISCAL_COUNCIL' | 'MEMBER'
  profile: UserProfile
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface LoginResponse {
  key: string
}

export interface RegistrationPayload {
  email: string
  password1: string
  password2: string
  first_name?: string
  last_name?: string
  phone?: string
}

export interface SetupPasswordPayload {
  token: string
  password: string
  password_confirm: string
}

export interface UpdatePreferencesPayload {
  theme_preference?: 'white' | 'black'
  language_preference?: 'pt-BR' | 'en' | 'es'
  membership_due_day?: number
  phone?: string
  country?: string
  city?: string
  state?: string
}

export interface VoluntaryDonation {
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

export interface VoluntaryDonationCreate {
  amount: number
  message?: string
  is_anonymous?: boolean
  payment_proof?: File
}

export interface DonationRequest {
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

export interface DonationRequestCreate {
  recipient_name: string
  recipient_description: string
  amount: number
  reason: string
  urgency_level: 'low' | 'medium' | 'high' | 'critical'
}

export interface MembershipFee {
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

export interface AttachmentPayload {
  case: number
  attachment_type: 'payment_proof' | 'photo_evidence' | 'other'
  file: File
}

class ApiService {
  private authToken: string | null

  constructor(private readonly baseUrl: string = API_BASE_URL) {
    this.authToken = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
  }

  private buildUrl(endpoint: string): string {
    if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) {
      return endpoint
    }
    const normalized = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
    return `${this.baseUrl}${normalized}`
  }

  private normaliseBody(body: unknown): BodyInit | undefined {
    if (body === undefined || body === null) return undefined
    if (body instanceof FormData || body instanceof Blob || typeof body === 'string') {
      return body
    }
    return JSON.stringify(body)
  }

  private extractError(payload: any): string | undefined {
    if (!payload) return undefined
    return payload.detail || payload.message || payload.error || undefined
  }

  async request<T = any>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    try {
      const url = this.buildUrl(endpoint)
      const headers = new Headers(options.headers ?? {})

      if (!headers.has('Accept')) {
        headers.set('Accept', 'application/json')
      }

      const token = this.authToken
      if (token && !headers.has('Authorization')) {
        headers.set('Authorization', `Token ${token}`)
      }

      const body = this.normaliseBody(options.body)
      if (body && !(body instanceof FormData) && !headers.has('Content-Type')) {
        headers.set('Content-Type', 'application/json')
      }

      const response = await fetch(url, {
        ...options,
        headers,
        body,
      })

      const contentType = response.headers.get('content-type')

      if (response.status === 204) {
        return { status: 204 }
      }

      if (contentType && contentType.includes('application/json')) {
        const payload = await response.json()
        if (!response.ok) {
          if (response.status === 401) {
            this.setAuthToken(null)
            if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
              window.location.href = '/login?expired=true'
            }
          }
          return {
            status: response.status,
            error: this.extractError(payload) ?? JSON.stringify(payload),
          }
        }
        return {
          status: response.status,
          data: payload as T,
        }
      }

      const fallback = await response.text()
      return {
        status: response.status,
        error: fallback || 'Unexpected response from server',
      }
    } catch (error) {
      return {
        status: 0,
        error: error instanceof Error ? error.message : 'Network error',
      }
    }
  }

  async get<T = any>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'GET' })
  }

  async post<T = any>(endpoint: string, body?: unknown, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'POST', body })
  }

  async patch<T = any>(endpoint: string, body?: unknown, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'PATCH', body })
  }

  async put<T = any>(endpoint: string, body?: unknown, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'PUT', body })
  }

  async delete<T = any>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' })
  }

  setAuthToken(token: string | null): void {
    this.authToken = token
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('auth_token', token)
      } else {
        localStorage.removeItem('auth_token')
      }
    }
  }

  getAuthToken(): string | null {
    return this.authToken
  }

  resolve(endpoint: string): string {
    return this.buildUrl(endpoint)
  }

  // ---------------------------------------------------------------------------
  // Auth & user profile
  // ---------------------------------------------------------------------------
  async login(credentials: LoginCredentials): Promise<ApiResponse<LoginResponse>> {
    return this.post<LoginResponse>('/auth/login/', credentials)
  }

  async logout(): Promise<ApiResponse> {
    return this.post('/auth/logout/', {})
  }

  async currentUser(): Promise<ApiResponse<User>> {
    return this.get<User>('/users/me/')
  }

  async register(data: RegistrationPayload): Promise<ApiResponse<LoginResponse>> {
    return this.post<LoginResponse>('/auth/registration/', data)
  }

  async submitOnboarding(data: OnboardingData): Promise<ApiResponse> {
    return this.post('/users/onboarding/', data)
  }

  async validateInvitationToken(token: string): Promise<ApiResponse> {
    return this.post('/users/invitations/validate-token/', { token })
  }

  async setupPassword(data: SetupPasswordPayload): Promise<ApiResponse<{ user: User; token: string }>> {
    return this.post('/users/invitations/setup-password/', data)
  }

  async updatePreferences(data: UpdatePreferencesPayload): Promise<ApiResponse<UserProfile>> {
    return this.patch('/users/preferences/', data)
  }

  // ---------------------------------------------------------------------------
  // Finance domain
  // ---------------------------------------------------------------------------
  async getMyFees(): Promise<ApiResponse<MembershipFee[]>> {
    return this.get('/finance/fees/my_fees/')
  }

  async getAllFees(): Promise<ApiResponse<MembershipFee[]>> {
    return this.get('/finance/fees/')
  }

  async createVoluntaryDonation(data: VoluntaryDonationCreate): Promise<ApiResponse<VoluntaryDonation>> {
    const formData = new FormData()
    formData.append('amount', data.amount.toString())
    if (data.message) formData.append('message', data.message)
    if (typeof data.is_anonymous !== 'undefined') {
      formData.append('is_anonymous', String(data.is_anonymous))
    }
    if (data.payment_proof) {
      formData.append('payment_proof', data.payment_proof)
    }
    return this.post('/finance/voluntary-donations/', formData)
  }

  async getMyVoluntaryDonations(): Promise<ApiResponse<VoluntaryDonation[]>> {
    return this.get('/finance/voluntary-donations/my_donations/')
  }

  async getAllVoluntaryDonations(): Promise<ApiResponse<VoluntaryDonation[]>> {
    return this.get('/finance/voluntary-donations/')
  }

  async getPendingVoluntaryDonations(): Promise<ApiResponse<VoluntaryDonation[]>> {
    return this.get('/finance/voluntary-donations/pending_verification/')
  }

  async verifyVoluntaryDonation(id: number): Promise<ApiResponse<VoluntaryDonation>> {
    return this.post(`/finance/voluntary-donations/${id}/verify/`)
  }

  async createDonationRequest(data: DonationRequestCreate): Promise<ApiResponse<DonationRequest>> {
    return this.post('/finance/donation-requests/', data)
  }

  async updateDonationRequest(id: number, data: Partial<DonationRequestCreate>): Promise<ApiResponse<DonationRequest>> {
    return this.patch(`/finance/donation-requests/${id}/`, data)
  }

  async deleteDonationRequest(id: number): Promise<ApiResponse> {
    return this.delete(`/finance/donation-requests/${id}/`)
  }

  async getMyDonationRequests(): Promise<ApiResponse<DonationRequest[]>> {
    return this.get('/finance/donation-requests/my_requests/')
  }

  async getAllDonationRequests(): Promise<ApiResponse<DonationRequest[]>> {
    return this.get('/finance/donation-requests/')
  }

  async getPendingDonationRequests(): Promise<ApiResponse<DonationRequest[]>> {
    return this.get('/finance/donation-requests/pending_approval/')
  }

  async approveDonationRequest(id: number): Promise<ApiResponse<DonationRequest>> {
    return this.post(`/finance/donation-requests/${id}/approve/`)
  }

  async rejectDonationRequest(id: number, reason: string): Promise<ApiResponse<DonationRequest>> {
    return this.post(`/finance/donation-requests/${id}/reject/`, { rejection_reason: reason })
  }

  async getDonationRequestStats(): Promise<ApiResponse<any>> {
    return this.get('/finance/donation-requests/stats/')
  }

  // ---------------------------------------------------------------------------
  // Assistance domain
  // ---------------------------------------------------------------------------
  async getAssistanceCases(params: string = ''): Promise<ApiResponse<any>> {
    return this.get(`/assistance/cases/${params}`)
  }

  async getAssistanceCase(id: number): Promise<ApiResponse<any>> {
    return this.get(`/assistance/cases/${id}/`)
  }

  async submitBankInfo(caseId: number, bankData: Record<string, unknown>): Promise<ApiResponse<any>> {
    return this.post(`/assistance/cases/${caseId}/submit_bank_info/`, bankData)
  }

  async confirmTransfer(caseId: number): Promise<ApiResponse<any>> {
    return this.post(`/assistance/cases/${caseId}/confirm_transfer/`)
  }

  async submitMemberProof(caseId: number): Promise<ApiResponse<any>> {
    return this.post(`/assistance/cases/${caseId}/submit_member_proof/`)
  }

  async completeCase(caseId: number): Promise<ApiResponse<any>> {
    return this.post(`/assistance/cases/${caseId}/complete/`)
  }

  async uploadAttachment(payload: AttachmentPayload): Promise<ApiResponse<any>> {
    const formData = new FormData()
    formData.append('case', payload.case.toString())
    formData.append('attachment_type', payload.attachment_type)
    formData.append('file', payload.file)
    return this.post('/assistance/attachments/', formData)
  }

  async deleteAttachment(attachmentId: number): Promise<ApiResponse<any>> {
    return this.delete(`/assistance/attachments/${attachmentId}/`)
  }
}

export const apiService = new ApiService()
export const api = apiService

export function buildApiUrl(endpoint: string): string {
  return apiService.resolve(endpoint)
}

export type {
  VoluntaryDonation,
  VoluntaryDonationCreate,
  DonationRequest,
  DonationRequestCreate,
  MembershipFee,
  ApiResponse,
  OnboardingData,
  User,
  UserProfile,
  LoginCredentials,
  LoginResponse,
  RegistrationPayload,
  SetupPasswordPayload,
  UpdatePreferencesPayload,
}
