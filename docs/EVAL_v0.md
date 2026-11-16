# Lab-Pocket Retrieval Evaluation v0

## Run status

Not run. The question set is recorded below, but answers and scores require a
populated pgvector database plus working embedding and chat API credentials.
No live results are inferred from unit tests. Record results here after running
each question against `POST /ask`.

## Scoring

Score each answer from 0 to 2 for correctness (0 = incorrect/unanswered,
1 = partially correct, 2 = correct) and citation support (0 = missing or
irrelevant, 1 = partly supported, 2 = source directly supports the answer).
Review answers against the cited source sections before assigning scores.

| # | Question | Correctness (0-2) | Citation support (0-2) | Result / notes |
|---|---|---:|---:|---|
| 1 | How does PWM work in ESP32? | N/R | N/R | Not run |
| 2 | How do I configure GPIO pins? | N/R | N/R | Not run |
| 3 | How can I read an analog sensor? | N/R | N/R | Not run |
| 4 | How do I connect an LED? | N/R | N/R | Not run |
| 5 | How does I2C communication work? | N/R | N/R | Not run |
| 6 | How do I use UART communication? | N/R | N/R | Not run |
| 7 | How can I connect a temperature sensor? | N/R | N/R | Not run |
| 8 | How do I control a servo motor? | N/R | N/R | Not run |
| 9 | How do I use interrupts in MicroPython? | N/R | N/R | Not run |
| 10 | How can I upload MicroPython code to Raspberry Pi Pico? | N/R | N/R | Not run |

`N/R` means not run and is not a score. Keep the question set and evaluation
criteria fixed when comparing later versions.