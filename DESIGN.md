# Lab-Pocket - System Design

## 1. Project Overview
Lab-Pocket is a lightweight MicroPython assistant for ECE students.

## 2. Architecture
- Frontend: Mobile-friendly interface
- Backend: Python FastAPI
- LLM: Primary model with fallback model
- Dataset: MicroPython source documentation
- Database: PostgreSQL with pgvector
- Deployment: Docker Compose

## 3. API Endpoints
- GET /health : Backend health check
- POST /chat : Submit board-related questions
- GET /usage : View token and cost usage

## 4. LLM Reliability
- Primary LLM provider
- Fallback LLM provider
- Request timeout
- Retry mechanism
- Error handling

## 5. Chat Request
{
  "board": "ESP32",
  "question": "How does PWM work?"
}

## 6. Chat Response
- board
- answer
- model_used
- input_tokens
- output_tokens
- total_tokens

## 7. Testing
- Pytest for backend tests
- Ruff for code quality
- GitHub Actions for CI

## 8. Deployment
Docker Compose will manage the API and PostgreSQL with pgvector.

## 9. Performance Goals
- Lightweight responses
- Low-bandwidth support
- Reliable LLM fallback
- Accurate MicroPython answers
