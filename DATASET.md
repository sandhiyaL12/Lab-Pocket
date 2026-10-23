# Dataset

| File | Source URL | Pages | Licence / terms | Downloaded on |
|------|------------|-------|-----------------|---------------|
| Core interpreter: `py/` (tag: shared) | https://github.com/micropython/micropython/tree/master/py | all files in folder | MIT | 23-10-2026 |
| Shared modules: `extmod/`, `shared/`, `drivers/` (tag: shared) | https://github.com/micropython/micropython/tree/master/extmod | all files in folders | MIT | 23-10-2026 |
| ESP32 port: `ports/esp32/` incl. `boards/` (tag: esp32) | https://github.com/micropython/micropython/tree/master/ports/esp32 | all files in folder | MIT | 23-10-2026 |
| RP2 / Pico port: `ports/rp2/` incl. `boards/` (tag: rp2) | https://github.com/micropython/micropython/tree/master/ports/rp2 | all files in folder | MIT | 23-10-2026 |
| Docs: `docs/library/`, `docs/esp32/`, `docs/rp2/` | https://github.com/micropython/micropython/tree/master/docs | all files in folders | MIT | 23-10-2026 |
| Tests / examples: `tests/ports/`, `tests/extmod/` | https://github.com/micropython/micropython/tree/master/tests | all files in folders | MIT | 23-10-2026 |

**Total:** 4,300+ source files (check with `git ls-files | wc -l` after cloning).

**Version:** MicroPython release tag `<TAG>`, commit `<SHA>` (fill in after cloning).

**Board tags:** every file is tagged `esp32`, `rp2` or `shared`. The board filter shows `esp32` + `shared`, or `rp2` + `shared`.

**Licence note:** MicroPython is MIT licensed. Keep the licence notice with any copied code.

Full data lives in `data/raw/` (not committed). A 2–3 file sample is in `data/sample/`.
