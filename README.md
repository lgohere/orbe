# ORBE Platform - MVP

Plataforma digital para gestão da ONG ORBE - ONG Real Bem-Estar.

## 🏗 Arquitetura

**Monorepo Structure:**
- `backend/` - Django REST API
- `frontend/` - Vue3 + TypeScript + TailwindCSS
- `docker/` - Docker configuration
- `docs/` - Documentation

## 🚀 Quick Start

### Development Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend
cd frontend
npm install
npm run dev
```

### Docker Setup

```bash
docker-compose up -d
```

## 📋 Features

- ✅ Google OAuth + Manual Authentication
- ✅ Multi-step Onboarding Wizard
- ✅ Monthly Fee Management (R$ 60.00)
- ✅ Donation System (PIX + QR Code)
- ✅ Assistance Cases (Document Upload Required)
- ✅ Approval Workflow (Board → Fiscal Council)
- ✅ Communication Feed (Social Media Style)
- ✅ Multi-language Support (PT-BR, EN, ES)
- ✅ White/Black Theme System
- ✅ Mobile-First Responsive Design
- ✅ Icon System (Lucide/Phosphor)
- ✅ Role-Based Access Control

## 🎯 MVP Goals

Construir o MVP funcional da plataforma ORBE com onboarding simplificado, gestão de mensalidades/doações via PIX, registro de atendimentos com comprovantes, feed responsivo, multilinguagem e temas customizáveis.

## 🛡 Security

- OAuth2 authentication
- Role-based permissions
- Secure file uploads
- CSRF protection
- SQL injection protection

## 🔧 Tech Stack

**Backend:**
- Django 4.2+
- Django REST Framework
- PostgreSQL
- Redis (Cache/Session)
- Celery (Background Tasks)
- django-allauth (OAuth)

**Frontend:**
- Vue 3 + Composition API
- TypeScript
- TailwindCSS
- Vue Router
- Vue I18n
- Unplugin Icons

**DevOps:**
- Docker + Docker Compose
- Nginx (Reverse Proxy)
- PostgreSQL Database
- Redis Cache