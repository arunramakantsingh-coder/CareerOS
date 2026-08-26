# CareerOS - AI-Powered Global Career Operating System

CareerOS is an intelligent career intelligence platform that helps professionals discover global opportunities, manage career personas, and navigate international careers.

## Project Status

**Foundation Phase Complete** ✅

The foundational architecture is in place with:
- Multi-tenant SaaS architecture
- PostgreSQL with pgvector-ready configuration
- FastAPI backend with health monitoring
- Next.js frontend with Tailwind CSS
- Docker Compose for local development
- Database migration framework with Alembic

## Prerequisites

- Docker Desktop (latest version)
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

## Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd CareerOS

##📊 Quick Reference Card
Service	URL	Purpose
Frontend	http://localhost:3000	Main application UI
API Root	http://localhost:8000	API information
API Docs	http://localhost:8000/docs	Interactive Swagger docs
Health	http://localhost:8000/api/v1/health	System health status
Ping	http://localhost:8000/api/v1/ping	Simple connectivity test
OpenAPI	http://localhost:8000/openapi.json	API schema
