# ORBE Platform - Implementation Guide

**Version**: 2.0
**Last Updated**: October 3, 2025
**Implementation Status**: ~85% Complete
**Author**: Principal Implementation Software Engineer & Architect

---

## 📋 Executive Summary

This document provides a comprehensive guide to the ORBE Platform's current implementation state. The platform is a social NGO management system for ORBE (ONG Real Bem-Estar) located in Baixada Santista, Brazil.

### Technology Stack

**Backend**:
- Django 4.2.7 + Django REST Framework 3.14.0
- PostgreSQL 15 (production) / SQLite (development)
- Redis 7 (cache, sessions, Celery broker)
- Celery 5.3.4 + Celery Beat (background tasks)
- django-allauth 0.57.0 (authentication + Google OAuth2)
- boto3 + django-storages (Hetzner Object Storage/S3)

**Frontend**:
- Vue 3.4.21 (Composition API + TypeScript 5.4.3)
- Vuetify 3.5.17 (Material Design 3)
- Pinia 2.1.7 (state management)
- Vue Router 4.3.0
- Vue I18n 9.10.2 (PT-BR, EN, ES)
- Vite 5.4.11 (build tool)

**Infrastructure**:
- Docker Compose (6 services: db, redis, backend, frontend, celery, celery-beat)
- n8n + RabbitMQ (external email automation)
- Hetzner VPS (production deployment target)

---

## 🎯 Implementation Status: 85% Complete

### ✅ Fully Implemented Features (85%)

#### 1. Authentication & User Management (100%)
- ✅ Custom User model with role-based access (SUPER_ADMIN, BOARD, FISCAL_COUNCIL, MEMBER)
- ✅ Google OAuth2 integration via django-allauth
- ✅ Token authentication (DRF) + Session authentication
- ✅ Login/logout flow with Pinia store
- ✅ Password reset via email
- ✅ Email invitation system with InvitationToken model
- ✅ n8n + RabbitMQ webhook integration for automated invitations
- ✅ SetPasswordView for first-time password setup
- ✅ Auto-login after password setup

**Key Files**:
- `backend/users/models.py` - User, UserProfile, InvitationToken models
- `backend/users/views.py` - UserViewSet, SetPasswordView, InvitationCreateView
- `frontend/src/stores/auth.ts` - Pinia auth store with token management
- `frontend/src/views/LoginView.vue` - Login page with Google OAuth

#### 2. Onboarding System (100%)
- ✅ 4-step wizard (Personal Info → Address → Preferences → Terms)
- ✅ User-configurable membership due day (1-28)
- ✅ Theme selection (white/black) with live preview
- ✅ Language selection (PT-BR, EN, ES) with flags
- ✅ Terms of service & privacy policy acceptance
- ✅ API endpoint `/api/users/onboarding/` with validation
- ✅ Webhook notification to n8n on completion

**Key Files**:
- `frontend/src/views/OnboardingView.vue` - Main wizard container
- `frontend/src/components/onboarding/OnboardingStep[1-4].vue` - Individual steps
- `backend/users/serializers.py` - OnboardingSerializer with webhook integration

#### 3. Finance Module (100%)

##### A. Membership Fees
- ✅ MembershipFee model (user, competency_month, amount, due_date, status)
- ✅ Automatic fee generation (Celery task: generate_membership_fees)
- ✅ Configurable due date per user (from UserProfile.membership_due_day)
- ✅ Email reminders (D-0 and D+3) via Celery Beat
- ✅ Status tracking (pending, paid, overdue, cancelled)
- ✅ Admin interface for fee management
- ✅ API endpoints (`/api/finance/fees/`)
- ✅ PIX QR Code display in dashboard
- ✅ PixPaymentDialog component with copy-to-clipboard

**Celery Tasks**:
```python
# finance/tasks.py
@shared_task
def generate_membership_fees()  # Runs 1st of each month
@shared_task
def send_membership_reminders()  # Runs daily at 9 AM (D-0)
@shared_task
def send_overdue_reminders()     # Runs daily at 9 AM (D+3)
```

##### B. Voluntary Donations
- ✅ Donation model (user, amount, message, payment_proof, donated_at)
- ✅ **MANDATORY payment proof** (image/PDF, max 5MB)
- ✅ Optional amount (can be anonymous value)
- ✅ Optional message from donor
- ✅ Anonymous donation support (user nullable)
- ✅ Admin interface for donation tracking
- ✅ API endpoints (`/api/finance/donations/`)
- ✅ VoluntaryDonationDialog with PIX QR Code
- ✅ Currency formatting (automatic ,00 decimal places)
- ✅ PIX code copy-to-clipboard functionality

**Key Files**:
- `backend/finance/models.py` - MembershipFee, Donation models
- `backend/finance/tasks.py` - Celery tasks for reminders
- `backend/finance/admin.py` - Django admin configuration
- `frontend/src/components/finance/PixPaymentDialog.vue` - Membership PIX modal
- `frontend/src/components/donations/VoluntaryDonationDialog.vue` - Donation modal

#### 4. Assistance Cases Module (100%)

##### Workflow (8 States)
1. **draft** - Created by Board, not yet submitted
2. **pending_member_proof** - Waiting for member to upload payment proof
3. **pending_admin_validation** - Admin reviewing member proofs
4. **pending_board_completion** - Board adding final documentation
5. **pending_fiscal_approval** - Fiscal Council reviewing for approval
6. **approved** - Fiscal Council approved (published to feed)
7. **rejected** - Fiscal Council rejected
8. **completed** - Case finalized with all documentation

##### Features
- ✅ AssistanceCase model with 8-state workflow
- ✅ Role-based permissions (Board creates, Fiscal Council approves)
- ✅ File attachments (CaseAttachment model)
  - Board attachments (internal documentation)
  - Member attachments (payment proofs, max 5 files)
  - File validation (images/PDF, max 5MB)
- ✅ Timeline tracking (CaseTimeline model)
  - Auto-generated entries via Django signals
  - Manual notes by Board/Fiscal Council
- ✅ Automatic status transitions based on actions
- ✅ Email notifications via n8n webhooks
- ✅ Admin validation workflow
- ✅ Markdown formatting for descriptions (native Vue rendering)
- ✅ Month/year organization in case lists
- ✅ Badge counts for "Em Andamento" and "Concluídos" tabs

**State Transition Logic**:
```python
# When member uploads proof → pending_admin_validation
# When admin validates → pending_board_completion
# When board completes → pending_fiscal_approval
# When fiscal approves → approved
# When fiscal rejects → rejected
```

**Permission System**:
- **Board**: Create drafts, submit, complete, view all cases
- **Fiscal Council**: Approve/reject, view all cases
- **Admin**: Validate member proofs, view all cases
- **Members**: View assigned cases, upload proofs (max 5 files), delete own attachments only

**Key Files**:
- `backend/assistance/models.py` - AssistanceCase, CaseAttachment, CaseTimeline
- `backend/assistance/views.py` - CaseViewSet with 8-state workflow actions
- `backend/assistance/signals.py` - Auto-timeline generation
- `frontend/src/views/cases/CaseDetailView.vue` - Case detail with markdown rendering
- `frontend/src/views/cases/CasesListView.vue` - Cases organized by month/year
- `frontend/src/views/cases/CreateCaseView.vue` - Board case creation form

#### 5. Dashboard (100%)
- ✅ Role-based dashboard (different views per role)
- ✅ Quick actions (Fazer Doação, Gerar PIX, Ver Casos, etc.)
- ✅ Financial stats cards (pending fees, donations, total collected)
- ✅ Assistance cases stats (active, completed)
- ✅ Real-time data loading with proper error handling
- ✅ Integration with PixPaymentDialog and VoluntaryDonationDialog
- ✅ Responsive design (mobile-first)

**Key Files**:
- `frontend/src/views/DashboardView.vue` - Main dashboard component

#### 6. Internationalization (100%)
- ✅ Vue I18n configured with 3 locales
- ✅ Portuguese (PT-BR) - Default language
- ✅ English (EN)
- ✅ Spanish (ES)
- ✅ Language selector with flags
- ✅ Browser language detection
- ✅ Persistent language preference (UserProfile.language_preference)
- ✅ Complete translations for all UI elements

**Key Files**:
- `frontend/src/locales/pt-BR.json` - Portuguese translations
- `frontend/src/locales/en.json` - English translations
- `frontend/src/locales/es.json` - Spanish translations
- `frontend/src/main.ts` - i18n configuration

#### 7. Theming System (100%)
- ✅ Custom ORBE themes defined
- ✅ **White Theme** (default):
  - Primary: #304E69 (deep blue)
  - Secondary: #C79657 (gold/bronze)
  - Background: #DDEAF4 (light blue gradient)
  - Surface: #FFFFFF (white cards)
- ✅ **Black Theme**:
  - Primary: #5B7185 (steel blue)
  - Secondary: #C79657 (gold/bronze)
  - Background: #304E69 (dark blue gradient)
  - Surface: #5B7185 (dark steel cards)
- ✅ Theme selection in onboarding
- ✅ Theme persistence (UserProfile.theme_preference)

**Key Files**:
- `frontend/src/main.ts` - Vuetify theme configuration (lines 84-129)

---

### ⚠️ Partially Implemented (5%)

#### 8. Feed/Communication System (20%)
- ✅ Post model structure defined in spec
- ⚠️ No API endpoints implemented
- ❌ No frontend components
- ❌ No post creation workflow

**Required Implementation**:
```python
# backend/feed/models.py
class Post(models.Model):
    type = models.CharField(choices=['announcement', 'financial_report', 'assistance_case'])
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='feed_images/%Y/%m/', null=True, blank=True)
    assistance_case = models.ForeignKey(AssistanceCase, null=True, blank=True)
    published_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
```

#### 9. Theme Toggle UI (50%)
- ✅ Themes fully defined in Vuetify config
- ✅ Theme selection in onboarding works
- ⚠️ No header toggle button implemented
- ❌ No real-time theme switching after login

**Required Implementation**:
- Create theme toggle component in app header
- Implement theme switching without page reload
- Sync theme changes with API (update UserProfile)

---

### ❌ Not Implemented (10%)

#### 10. Production Deployment Configuration (0%)
- ❌ No production Dockerfile (multi-stage build)
- ❌ No Nginx configuration
- ❌ No SSL/HTTPS setup
- ❌ No static file collection setup
- ❌ No production docker-compose.yml
- ❌ No CI/CD pipeline

#### 11. Advanced Email Templates (30%)
- ✅ Invitation email (via n8n)
- ⚠️ Membership reminder email (basic, needs HTML template)
- ❌ Overdue reminder email (no template)
- ❌ Case notification emails (no templates)

#### 12. Comprehensive Testing (10%)
- ⚠️ Basic Django tests exist but incomplete
- ❌ No frontend unit tests
- ❌ No E2E tests
- ❌ No integration tests for critical workflows

---

## 🏗️ Architecture Deep Dive

### Backend Architecture

#### Django Apps Structure

```
backend/
├── orbe_platform/          # Main Django project
│   ├── settings.py         # Configuration with env-based settings
│   ├── urls.py             # Root URL configuration
│   ├── celery.py           # Celery configuration
│   └── wsgi.py             # WSGI entry point
│
├── users/                  # User management & authentication
│   ├── models.py           # User, UserProfile, InvitationToken
│   ├── serializers.py      # API serializers with webhook integration
│   ├── views.py            # ViewSets and custom views
│   ├── admin.py            # Django admin configuration
│   └── signals.py          # Auto-create UserProfile on User creation
│
├── finance/                # Financial management
│   ├── models.py           # MembershipFee, Donation
│   ├── serializers.py      # API serializers with validation
│   ├── views.py            # ViewSets with role-based permissions
│   ├── admin.py            # Django admin with custom actions
│   └── tasks.py            # Celery tasks (reminders, fee generation)
│
├── assistance/             # Assistance cases management
│   ├── models.py           # AssistanceCase, CaseAttachment, CaseTimeline
│   ├── serializers.py      # Nested serializers for attachments/timeline
│   ├── views.py            # CaseViewSet with 8-state workflow
│   ├── admin.py            # Django admin with workflow actions
│   └── signals.py          # Auto-timeline generation
│
└── feed/                   # Communication feed (NOT IMPLEMENTED)
    ├── models.py           # Empty
    ├── serializers.py      # Empty
    ├── views.py            # Empty
    └── admin.py            # Empty
```

#### Key Models

**User Model** (`users/models.py`):
```python
class User(AbstractUser):
    username = None  # Removed
    email = models.EmailField(unique=True)  # USERNAME_FIELD
    role = models.CharField(
        max_length=20,
        choices=[
            ('SUPER_ADMIN', 'Super Admin'),
            ('BOARD', 'Board Member'),
            ('FISCAL_COUNCIL', 'Fiscal Council'),
            ('MEMBER', 'Member')
        ],
        default='MEMBER'
    )

    # Computed properties
    @property
    def is_board_member(self):
        return self.role in ['SUPER_ADMIN', 'BOARD']

    @property
    def can_approve_cases(self):
        return self.role in ['SUPER_ADMIN', 'FISCAL_COUNCIL']
```

**UserProfile Model** (`users/models.py`):
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Brasil')

    membership_due_day = models.IntegerField(default=10, validators=[
        MinValueValidator(1), MaxValueValidator(28)
    ])
    theme_preference = models.CharField(max_length=10, choices=[
        ('white', 'White'), ('black', 'Black')
    ], default='white')
    language_preference = models.CharField(max_length=5, choices=[
        ('pt-BR', 'Português'), ('en', 'English'), ('es', 'Español')
    ], default='pt-BR')

    is_onboarding_completed = models.BooleanField(default=False)
```

**MembershipFee Model** (`finance/models.py`):
```python
class MembershipFee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='membership_fees')
    competency_month = models.DateField()  # e.g., 2025-01-01
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=60.00)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'competency_month')
        ordering = ['-competency_month']
```

**AssistanceCase Model** (`assistance/models.py`):
```python
class AssistanceCase(models.Model):
    title = models.CharField(max_length=200)
    public_description = models.TextField()
    internal_description = models.TextField()
    total_value = models.DecimalField(max_digits=10, decimal_places=2)
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assistance_cases')
    status = models.CharField(max_length=30, choices=[
        ('draft', 'Draft'),
        ('pending_member_proof', 'Pending Member Proof'),
        ('pending_admin_validation', 'Pending Admin Validation'),
        ('pending_board_completion', 'Pending Board Completion'),
        ('pending_fiscal_approval', 'Pending Fiscal Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed')
    ], default='draft')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_cases')
    reviewed_by = models.ForeignKey(User, null=True, blank=True, related_name='reviewed_cases')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
```

#### Celery Tasks

**Location**: `backend/finance/tasks.py`

```python
from celery import shared_task
from celery.schedules import crontab
from datetime import date, timedelta
from django.utils import timezone

@shared_task
def generate_membership_fees():
    """
    Generate membership fees for all active users.
    Runs on the 1st of each month at midnight.
    """
    from users.models import User
    from finance.models import MembershipFee

    today = date.today()
    competency = date(today.year, today.month, 1)

    for user in User.objects.filter(is_active=True):
        due_day = user.profile.membership_due_day
        due_date = date(today.year, today.month, min(due_day, 28))

        MembershipFee.objects.get_or_create(
            user=user,
            competency_month=competency,
            defaults={
                'amount': 60.00,
                'due_date': due_date,
                'status': 'pending'
            }
        )

@shared_task
def send_membership_reminders():
    """
    Send D-0 reminders (due date = today).
    Runs daily at 9 AM.
    """
    from finance.models import MembershipFee
    import requests

    today = date.today()
    fees = MembershipFee.objects.filter(
        due_date=today,
        status='pending',
        reminder_sent_at__isnull=True
    )

    for fee in fees:
        # Send via n8n webhook
        requests.post('https://n8n.texts.com.br/webhook/orbe_membership_reminder', json={
            'user_email': fee.user.email,
            'user_name': fee.user.first_name,
            'amount': str(fee.amount),
            'due_date': fee.due_date.isoformat(),
            'language': fee.user.profile.language_preference
        }, timeout=10)

        fee.reminder_sent_at = timezone.now()
        fee.save()

@shared_task
def send_overdue_reminders():
    """
    Send D+3 reminders (3 days overdue).
    Runs daily at 9 AM.
    """
    from finance.models import MembershipFee
    import requests

    three_days_ago = date.today() - timedelta(days=3)
    fees = MembershipFee.objects.filter(
        due_date=three_days_ago,
        status='overdue'
    )

    for fee in fees:
        requests.post('https://n8n.texts.com.br/webhook/orbe_overdue_reminder', json={
            'user_email': fee.user.email,
            'user_name': fee.user.first_name,
            'amount': str(fee.amount),
            'days_overdue': 3,
            'language': fee.user.profile.language_preference
        }, timeout=10)
```

**Celery Beat Schedule** (`backend/orbe_platform/celery.py`):
```python
app.conf.beat_schedule = {
    'generate-membership-fees': {
        'task': 'finance.tasks.generate_membership_fees',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),  # 1st of month, midnight
    },
    'send-membership-reminders': {
        'task': 'finance.tasks.send_membership_reminders',
        'schedule': crontab(hour=9, minute=0),  # Every day at 9 AM
    },
    'send-overdue-reminders': {
        'task': 'finance.tasks.send_overdue_reminders',
        'schedule': crontab(hour=9, minute=0),  # Every day at 9 AM
    },
}
```

---

### Frontend Architecture

#### Directory Structure

```
frontend/src/
├── main.ts                 # App initialization, Vuetify/i18n config
├── App.vue                 # Root component
├── router/
│   └── index.ts            # Vue Router with auth guards
│
├── stores/
│   └── auth.ts             # Pinia auth store (token, user, login/logout)
│
├── services/
│   └── api.ts              # API service layer (fetch-based)
│
├── views/
│   ├── LoginView.vue       # Login page with Google OAuth
│   ├── OnboardingView.vue  # 4-step onboarding wizard
│   ├── DashboardView.vue   # Main dashboard (role-based)
│   ├── SetPasswordView.vue # First-time password setup
│   ├── cases/
│   │   ├── CasesListView.vue      # Cases list with month/year grouping
│   │   ├── CaseDetailView.vue     # Case detail with markdown rendering
│   │   └── CreateCaseView.vue     # Board case creation form
│   └── finance/
│       └── FinanceView.vue        # Finance management (admin only)
│
├── components/
│   ├── onboarding/
│   │   ├── OnboardingStep1.vue    # Personal info
│   │   ├── OnboardingStep2.vue    # Address
│   │   ├── OnboardingStep3.vue    # Preferences
│   │   └── OnboardingStep4.vue    # Terms acceptance
│   ├── finance/
│   │   └── PixPaymentDialog.vue   # PIX payment modal
│   └── donations/
│       └── VoluntaryDonationDialog.vue  # Donation modal
│
├── locales/
│   ├── pt-BR.json          # Portuguese translations
│   ├── en.json             # English translations
│   └── es.json             # Spanish translations
│
└── styles/
    └── main.css            # Global styles
```

#### API Service Layer

**Location**: `frontend/src/services/api.ts`

```typescript
class ApiService {
  private baseURL = '/api'
  private authToken: string | null = null

  setAuthToken(token: string | null) {
    this.authToken = token
  }

  private async request(endpoint: string, options: RequestInit = {}): Promise<any> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(this.authToken && { 'Authorization': `Token ${this.authToken}` }),
      ...options.headers
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Request failed')
    }

    return response.json()
  }

  // Authentication
  async login(email: string, password: string) {
    return this.request('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    })
  }

  async logout() {
    return this.request('/auth/logout/', { method: 'POST' })
  }

  // User
  async getCurrentUser() {
    return this.request('/users/me/')
  }

  // Onboarding
  async submitOnboarding(data: OnboardingData) {
    return this.request('/users/onboarding/', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  // Finance
  async getMembershipFees() {
    return this.request('/finance/fees/')
  }

  async createDonation(formData: FormData) {
    return fetch(`${this.baseURL}/finance/donations/`, {
      method: 'POST',
      headers: {
        ...(this.authToken && { 'Authorization': `Token ${this.authToken}` })
      },
      body: formData
    })
  }

  // Assistance Cases
  async getCases(params?: Record<string, any>) {
    const queryString = new URLSearchParams(params).toString()
    return this.request(`/assistance/cases/${queryString ? `?${queryString}` : ''}`)
  }

  async createCase(data: any) {
    return this.request('/assistance/cases/', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }
}

export default new ApiService()
```

#### Pinia Auth Store

**Location**: `frontend/src/stores/auth.ts`

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const user = ref<User | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const isBoardMember = computed(() =>
    user.value?.role === 'SUPER_ADMIN' || user.value?.role === 'BOARD'
  )
  const canApprove = computed(() =>
    user.value?.role === 'SUPER_ADMIN' || user.value?.role === 'FISCAL_COUNCIL'
  )

  async function login(email: string, password: string) {
    try {
      loading.value = true
      const response = await api.login(email, password)

      token.value = response.key
      user.value = response.user

      localStorage.setItem('auth_token', response.key)
      api.setAuthToken(response.key)

      return response
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await api.logout()
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('auth_token')
      api.setAuthToken(null)
    }
  }

  async function fetchUser() {
    if (!token.value) return

    try {
      loading.value = true
      user.value = await api.getCurrentUser()
    } catch (error) {
      console.error('Failed to fetch user:', error)
      logout()
    } finally {
      loading.value = false
    }
  }

  // Initialize
  if (token.value) {
    api.setAuthToken(token.value)
    fetchUser()
  }

  return {
    token,
    user,
    loading,
    isAuthenticated,
    isBoardMember,
    canApprove,
    login,
    logout,
    fetchUser
  }
})
```

---

## 🔧 Infrastructure

### Docker Compose Services

**Location**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: orbe
      POSTGRES_USER: orbe
      POSTGRES_PASSWORD: orbe_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      DATABASE_URL: postgresql://orbe:orbe_password@db:5432/orbe
      REDIS_URL: redis://redis:6379/0
      DEBUG: "True"

  frontend:
    build: ./frontend
    command: npm run dev -- --host
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    depends_on:
      - backend

  celery:
    build: ./backend
    command: celery -A orbe_platform worker -l info
    volumes:
      - ./backend:/app
    depends_on:
      - db
      - redis
    environment:
      DATABASE_URL: postgresql://orbe:orbe_password@db:5432/orbe
      REDIS_URL: redis://redis:6379/0

  celery-beat:
    build: ./backend
    command: celery -A orbe_platform beat -l info
    volumes:
      - ./backend:/app
    depends_on:
      - db
      - redis
    environment:
      DATABASE_URL: postgresql://orbe:orbe_password@db:5432/orbe
      REDIS_URL: redis://redis:6379/0

volumes:
  postgres_data:
```

---

## 🔑 Key Implementation Patterns

### 1. Invitation System with n8n Webhook

**Backend** (`users/serializers.py`):
```python
def _send_webhook_notification(self, invitation):
    webhook_url = "https://n8n.texts.com.br/webhook/orbe_invitation"
    payload = {
        "email": invitation.email,
        "first_name": invitation.first_name,
        "token": invitation.token,
        "language": invitation.language or "pt-BR",
        "setup_url": f"https://orbe.com/set-password/{invitation.token}/"
    }
    try:
        requests.post(webhook_url, json=payload, timeout=10)
    except Exception as e:
        logger.error(f"Failed to send webhook: {e}")
        # Don't raise - invitation creation should succeed even if webhook fails
```

### 2. Timeline Tracking via Django Signals

**Backend** (`assistance/signals.py`):
```python
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import AssistanceCase, CaseAttachment, CaseTimeline

@receiver(post_save, sender=AssistanceCase)
def create_timeline_on_status_change(sender, instance, created, **kwargs):
    if created:
        CaseTimeline.objects.create(
            case=instance,
            user=instance.created_by,
            action='created',
            description=f'Case created with status: {instance.get_status_display()}'
        )
    else:
        # Check if status changed
        old_instance = AssistanceCase.objects.filter(pk=instance.pk).first()
        if old_instance and old_instance.status != instance.status:
            CaseTimeline.objects.create(
                case=instance,
                user=instance.created_by,
                action='status_changed',
                description=f'Status changed from {old_instance.get_status_display()} to {instance.get_status_display()}'
            )

@receiver(post_delete, sender=CaseAttachment)
def create_timeline_on_attachment_delete(sender, instance, **kwargs):
    CaseTimeline.objects.create(
        case=instance.case,
        user=instance.uploaded_by,
        action='attachment_deleted',
        description=f'Deleted attachment: {instance.file_name}'
    )
```

### 3. Role-Based Permissions

**Backend** (`assistance/views.py`):
```python
class CaseViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user = self.request.user

        if user.role in ['SUPER_ADMIN', 'BOARD', 'FISCAL_COUNCIL']:
            return AssistanceCase.objects.all()
        else:
            # Members only see cases assigned to them
            return AssistanceCase.objects.filter(member=user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        case = self.get_object()

        # Only Fiscal Council can approve
        if request.user.role not in ['SUPER_ADMIN', 'FISCAL_COUNCIL']:
            return Response({'error': 'Permission denied'}, status=403)

        case.status = 'approved'
        case.reviewed_by = request.user
        case.approved_at = timezone.now()
        case.save()

        # Send webhook notification
        self._send_approval_notification(case)

        return Response({'status': 'approved'})
```

### 4. Native Vue Markdown Rendering

**Frontend** (`views/cases/CaseDetailView.vue`):
```typescript
const formattedInternalDescription = computed(() => {
  if (!caseData.value?.internal_description) return ''

  let html = caseData.value.internal_description

  // Escape HTML to prevent XSS
  html = html
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // Convert markdown patterns to HTML
  // **bold** → <strong>bold</strong>
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')

  // *italic* → <em>italic</em>
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')

  // Line breaks → <br>
  html = html.replace(/\n/g, '<br>')

  return html
})
```

### 5. Currency Formatting with Automatic Decimal Places

**Frontend** (`components/donations/VoluntaryDonationDialog.vue`):
```typescript
const formattedAmount = ref('')

function formatCurrency(event: any) {
  let value = event.target.value
  value = value.replace(/[^\d,]/g, '')  // Only numbers and comma

  const parts = value.split(',')
  if (parts.length > 2) {
    value = parts[0] + ',' + parts.slice(1).join('')
  }

  if (parts.length === 2 && parts[1].length > 2) {
    value = parts[0] + ',' + parts[1].substring(0, 2)
  }

  formattedAmount.value = value
  form.amount = parseFloat(value.replace(',', '.')) || 0
}

function addDecimalPlaces() {
  if (!formattedAmount.value) return

  let value = formattedAmount.value

  if (!value.includes(',')) {
    value = value + ',00'
  } else {
    const parts = value.split(',')
    if (parts[1].length === 0) {
      value = parts[0] + ',00'
    } else if (parts[1].length === 1) {
      value = parts[0] + ',' + parts[1] + '0'
    }
  }

  formattedAmount.value = value
  form.amount = parseFloat(value.replace(',', '.')) || 0
}
```

---

## 📡 API Endpoints Reference

### Authentication & Users

```
POST   /api/auth/login/                    # Login (email + password)
POST   /api/auth/logout/                   # Logout
POST   /api/auth/registration/             # Manual registration
POST   /api/auth/password/reset/           # Password reset request
POST   /api/auth/password/reset/confirm/   # Password reset confirmation
GET    /accounts/google/login/             # Google OAuth2 redirect

GET    /api/users/me/                      # Current user details
PATCH  /api/users/me/                      # Update current user
POST   /api/users/onboarding/              # Complete onboarding
GET    /api/users/onboarding/status/       # Check onboarding status
PATCH  /api/users/preferences/             # Update preferences

POST   /api/users/invitations/             # Create invitation (admin only)
POST   /api/users/set-password/            # Set password from invitation
```

### Finance

```
GET    /api/finance/fees/                  # List membership fees
GET    /api/finance/fees/:id/              # Get fee detail
PATCH  /api/finance/fees/:id/              # Update fee (admin only)
POST   /api/finance/fees/:id/mark-paid/    # Mark fee as paid (admin only)

GET    /api/finance/donations/             # List donations
POST   /api/finance/donations/             # Create donation (with proof)
GET    /api/finance/donations/:id/         # Get donation detail
```

### Assistance Cases

```
GET    /api/assistance/cases/                      # List cases (role-filtered)
POST   /api/assistance/cases/                      # Create case (Board only)
GET    /api/assistance/cases/:id/                  # Get case detail
PATCH  /api/assistance/cases/:id/                  # Update case
DELETE /api/assistance/cases/:id/                  # Delete case (Board only)

POST   /api/assistance/cases/:id/submit/           # Submit draft → pending_member_proof
POST   /api/assistance/cases/:id/validate/         # Admin validate → pending_board_completion
POST   /api/assistance/cases/:id/complete/         # Board complete → pending_fiscal_approval
POST   /api/assistance/cases/:id/approve/          # Fiscal approve → approved
POST   /api/assistance/cases/:id/reject/           # Fiscal reject → rejected
POST   /api/assistance/cases/:id/add-note/         # Add timeline note

POST   /api/assistance/attachments/                # Upload attachment
DELETE /api/assistance/attachments/:id/            # Delete attachment (own only)

GET    /api/assistance/cases/:id/timeline/         # Get case timeline
```

### Admin & Documentation

```
GET    /admin/                             # Django admin panel
GET    /api/schema/                        # OpenAPI schema
GET    /api/docs/                          # Swagger UI documentation
```

---

## 🚀 Development Workflow

### Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd orbe

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

# Frontend setup
cd ../frontend
npm install

# Docker setup (alternative)
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

### Running Development Servers

**Option 1: Native** (recommended for development)
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python manage.py runserver

# Terminal 2 - Frontend
cd frontend
npm run dev

# Terminal 3 - Celery Worker (optional)
cd backend
source venv/bin/activate
celery -A orbe_platform worker -l info

# Terminal 4 - Celery Beat (optional)
cd backend
source venv/bin/activate
celery -A orbe_platform beat -l info
```

**Option 2: Docker**
```bash
docker-compose up
```

### Running Tests

```bash
# Backend tests
cd backend
source venv/bin/activate
pytest

# Frontend tests (when implemented)
cd frontend
npm run test

# E2E tests (when implemented)
npm run test:e2e
```

### Database Management

```bash
# Create migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (SQLite)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser

# Shell access
python manage.py shell

# List all users
python manage.py shell -c "from users.models import User; [print(u.email, u.role) for u in User.objects.all()]"
```

### Code Quality

```bash
# Backend linting
cd backend
flake8 .
black .
mypy .

# Frontend linting
cd frontend
npm run lint
npm run type-check
```

---

## ⚙️ Configuration Files

### Backend Environment Variables

**Development** (`.env`):
```bash
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0

# Google OAuth2
GOOGLE_OAUTH2_CLIENT_ID=your-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-client-secret

# Email (via n8n webhook)
N8N_WEBHOOK_BASE_URL=https://n8n.texts.com.br/webhook
```

**Production** (`.env.production`):
```bash
DEBUG=False
SECRET_KEY=<strong-random-key>
DATABASE_URL=postgresql://user:password@host:5432/orbe
REDIS_URL=redis://host:6379/0
ALLOWED_HOSTS=orbe.com,www.orbe.com

# S3/Object Storage
AWS_ACCESS_KEY_ID=<hetzner-access-key>
AWS_SECRET_ACCESS_KEY=<hetzner-secret-key>
AWS_STORAGE_BUCKET_NAME=orbe-storage
AWS_S3_ENDPOINT_URL=https://fsn1.your-objectstorage.com

# Google OAuth2
GOOGLE_OAUTH2_CLIENT_ID=<production-client-id>
GOOGLE_OAUTH2_CLIENT_SECRET=<production-client-secret>
```

### Frontend Environment Variables

**Development** (`.env.development`):
```bash
VITE_API_BASE_URL=http://localhost:8000
```

**Production** (`.env.production`):
```bash
VITE_API_BASE_URL=https://api.orbe.com
```

---

## 📋 Next Steps (Remaining 15%)

### Priority 1: Feed/Communication System (1 week)
1. Implement Post model with relationships
2. Create API endpoints for post CRUD
3. Build feed components (FeedView, PostCard)
4. Implement infinite scroll/pagination
5. Add post creation forms for Board/Admin
6. Integrate approved assistance cases into feed

### Priority 2: Theme Toggle UI (2 days)
1. Create ThemeToggle component for app header
2. Implement real-time theme switching
3. Sync theme changes with API (UserProfile)
4. Add smooth transition animations
5. Test theme persistence across sessions

### Priority 3: Production Deployment (1 week)
1. Create production Dockerfile (multi-stage build)
2. Configure Nginx as reverse proxy
3. Set up SSL certificates (Let's Encrypt)
4. Configure static file serving (WhiteNoise or S3)
5. Create production docker-compose.yml
6. Set up CI/CD pipeline (GitHub Actions or GitLab CI)
7. Configure monitoring and logging (Sentry, ELK stack)
8. Performance testing and optimization

### Priority 4: Testing & Quality Assurance (1 week)
1. Write unit tests for all models
2. Write API integration tests
3. Write frontend unit tests (Vitest)
4. Implement E2E tests (Playwright or Cypress)
5. Security audit (OWASP Top 10)
6. Accessibility audit (WCAG AA compliance)
7. Performance audit (Lighthouse)

---

## 🐛 Known Issues & Technical Debt

### Critical
- ❌ No production deployment configuration
- ❌ Missing comprehensive test coverage (<20%)
- ❌ No rate limiting on API endpoints
- ❌ No file size/type validation on uploads (partially implemented)

### Medium
- ⚠️ Theme toggle not in header (only in onboarding)
- ⚠️ No feed/communication system implemented
- ⚠️ Email templates need HTML formatting
- ⚠️ No error boundary components in frontend
- ⚠️ No loading states in some components

### Low
- ⚠️ No frontend caching strategy (service worker)
- ⚠️ No image optimization/compression
- ⚠️ No API response caching
- ⚠️ Console logs need removal in production
- ⚠️ TypeScript strict mode not fully enabled

---

## 📝 Code Style Guidelines

### Backend (Python/Django)

```python
# Follow PEP 8
# Use type hints
def calculate_due_date(user: User, competency: date) -> date:
    """Calculate due date based on user's preferred day."""
    due_day = user.profile.membership_due_day
    return date(competency.year, competency.month, min(due_day, 28))

# Use descriptive variable names
total_collected = MembershipFee.objects.filter(status='paid').aggregate(
    total=Sum('amount')
)['total']

# Keep functions small and focused
# Use docstrings for public methods
# Prefer composition over inheritance
```

### Frontend (TypeScript/Vue)

```typescript
// Use TypeScript strict mode
// Define interfaces for all data structures
interface User {
  id: number
  email: string
  role: UserRole
  profile: UserProfile
}

// Use Composition API with <script setup>
// Destructure only what you need from composables
const { t } = useI18n()
const authStore = useAuthStore()

// Use computed for derived state
const isAdmin = computed(() => authStore.user?.role === 'SUPER_ADMIN')

// Use meaningful component names (PascalCase)
// Props with default values and validation
defineProps<{
  title: string
  optional?: boolean
}>()

// Emit events with proper types
const emit = defineEmits<{
  submit: [data: FormData]
  cancel: []
}>()
```

---

## 🎓 Learning Resources

### Django + DRF
- [Django Documentation](https://docs.djangoproject.com/en/4.2/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryq.dev/en/stable/)

### Vue 3 + TypeScript
- [Vue 3 Documentation](https://vuejs.org/)
- [Vuetify 3 Documentation](https://vuetifyjs.com/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Vue I18n](https://vue-i18n.intlify.dev/)

### Infrastructure
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/docs/)

---

## 📞 Support & Contact

**Project**: ORBE Platform MVP
**Organization**: ORBE (ONG Real Bem-Estar)
**Location**: Baixada Santista, Brazil (Praia Grande/SP)
**Founded**: December 20, 2021

For technical questions or contributions, please refer to the project repository and follow the contribution guidelines.

---

**Document End**
