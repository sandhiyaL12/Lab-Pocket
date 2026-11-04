
# Lab-Pocket

**A Mobile-First MicroPython Helper for ECE Labs on Low-Bandwidth Networks**

[![GitHub](https://img.shields.io/badge/GitHub-Lab--Pocket-blue?logo=github)](https://github.com/sandhiyaL12/Lab-Pocket)

## Project Overview

Lab-Pocket is an AI-powered MicroPython assistant designed to help ECE students and lab instructors working with ESP32 and Raspberry Pi Pico boards.

It provides a lightweight API for answering board-specific MicroPython questions, especially in environments with slow or crowded internet connections.

## Problem Statement

ECE students often face difficulty finding correct MicroPython functions, pin configurations, and code examples while working in college laboratories. Slow Wi-Fi makes accessing large documentation websites inconvenient.

Lab-Pocket aims to provide a simple and lightweight solution for these problems.

## Target Users

- ECE and EEE students
- Polytechnic students
- Embedded systems beginners
- College lab instructors
- ESP32 and Raspberry Pi Pico developers

## Key Features

- FastAPI-based backend.
- Google Gemini API integration.
- Board-specific chat questions.
- ESP32 and Raspberry Pi Pico support.
- REST API endpoints.
- Interactive Swagger API documentation.
- Health monitoring endpoint.
- Docker support.
- Render cloud deployment.
- Designed for low-bandwidth environments.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Backend programming |
| FastAPI | API development |
| Google Gemini | AI integration |
| Docker | Containerization |
| Pytest | Automated testing |
| Ruff | Code quality |
| Git & GitHub | Version control |
| GitHub Actions | Continuous integration |
| Render | Cloud deployment |

## Dataset Sources

- [Official MicroPython Repository](https://github.com/micropython/micropython)
- [MicroPython Documentation](https://docs.micropython.org/)
- [ESP32 Documentation](https://docs.micropython.org/en/latest/esp32/quickref.html)
- [Raspberry Pi Pico Documentation](https://docs.micropython.org/en/latest/rp2/quickref.html)
- [STM32 MicroPython Documentation](https://docs.micropython.org/en/latest/stm32/quickref.html)

## Sample User Questions

1. How does PWM work in ESP32?
2. How do I configure GPIO pins?
3. How can I read an analog sensor?
4. How do I connect an LED?
5. How does I2C communication work?
6. How do I use UART communication?
7. How can I connect a temperature sensor?
8. How do I control a servo motor?
9. How do I use interrupts in MicroPython?
10. How can I upload MicroPython code to Raspberry Pi Pico?

## Project Structure

```text
Lab-Pocket/
│
├── app/
│   ├── main.py
│   └── ...
│
├── docs/
│   └── QUESTIONS.md
│
├── tools/
│   └── download.py
│
├── tests/
│
├── .github/
│   └── workflows/
│
├── Dockerfile
├── docker_compose.yml
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── .dockerignore
└── README.md
```

## Installation and Setup

### 1. Clone Repository

```bash
git clone https://github.com/sandhiyaL12/Lab-Pocket.git
cd Lab-Pocket
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Gemini API

Create a `.env` file in the project root directory.

Add the following configuration:

```env
PRIMARY_API_KEY=your_gemini_api_key
PRIMARY_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
PRIMARY_MODEL=your_configured_model
```

Replace the placeholders with your actual Gemini API key and configured model.

**Security:** Never upload your `.env` file or API keys to GitHub.

### 6. Run the Application

```bash
uvicorn app.main:app --reload
```

## API Documentation

After starting the application, open:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **Health Check:** http://127.0.0.1:8000/health

### Chat API

**Method:** POST

**Endpoint:** `/chat`

Example request:

```json
{
  "board": "ESP32",
  "question": "How does PWM work?"
}
```

## Live Deployment – Render

Lab-Pocket backend is deployed on Render.

| Resource | Link |
|---|---|
| Live API | [Open Live API](https://lab-pocket-new.onrender.com) |
| Swagger API Documentation | [Open API Docs](https://lab-pocket-new.onrender.com/docs) |
| Health Check | [Check API Health](https://lab-pocket-new.onrender.com/health) |

### Test the Live Deployment

1. Open the [Lab-Pocket Live API](https://lab-pocket-new.onrender.com).
2. Open the [Swagger API Documentation](https://lab-pocket-new.onrender.com/docs).
3. Find the `POST /chat` endpoint.
4. Click **Try it out**.
5. Enter the following request:

```json
{
  "board": "ESP32",
  "question": "How does PWM work?"
}
```

6. Click **Execute** to test the API.
7. Check the response displayed by Swagger UI.

## Docker Setup

### Build Docker Image

```bash
docker build -t lab-pocket .
```

### Run Docker Compose

```bash
docker compose up -d --build
```

### Check Running Containers

```bash
docker compose ps
```

### View Logs

```bash
docker compose logs -f
```

### Stop Containers

```bash
docker compose down
```

## Testing

### Run Automated Tests

```bash
python -m pytest -q
```

### Check Code Quality

```bash
ruff check .
```

### Check Formatting

```bash
ruff format --check .
```

### Run Pre-commit

```bash
pre-commit run --all-files
```

## Future Enhancements

- Develop a mobile-friendly chatbot interface.
- Add MicroPython documentation retrieval.
- Improve ESP32 and Raspberry Pi Pico support.
- Add verified code examples.
- Optimize API responses for low-bandwidth networks.
- Implement Retrieval-Augmented Generation (RAG).
- Add source-grounded answers.

## GitHub Repository

[Lab-Pocket – GitHub](https://github.com/sandhiyaL12/Lab-Pocket)

## Live Application

[Lab-Pocket – Render](https://lab-pocket-new.onrender.com)
