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
