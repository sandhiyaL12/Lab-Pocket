# Dataset

LabPocket's source corpus is a local checkout of the official
[MicroPython repository](https://github.com/micropython/micropython), release
`v1.29.0`, commit `0fd6c573ea815774668bbb16b8e197c8822368b2` (MIT-licensed).
It includes the shared interpreter, documentation,
examples, and ports including ESP32 and RP2.

| Collection | Source path | Use |
|---|---|---|
| Core interpreter | `py/`, `shared/`, `extmod/` | Shared runtime and modules |
| ESP32 | `ports/esp32/`, `docs/esp32/` | ESP32 implementation and board guidance |
| RP2 / Pico | `ports/rp2/`, `docs/rp2/` | RP2040 implementation and board guidance |
| Other ports | `ports/` | Cross-port comparison |
| Documentation | `docs/` | API and port reference |
| Tests and examples | `tests/`, `examples/` | Usage examples and implementation checks |

The local corpus contains 5,756 repository files, exceeding the project's
4,300-file collection target. It also contains 248 reStructuredText (`.rst`)
documentation pages. Its contents are kept out of Git; a small sample of four
source/license files is in `data/sample/`. Documentation uses source files and
headings rather than fixed page numbers. See
[docs/QUESTIONS.md](docs/QUESTIONS.md) for question-to-source references.

MicroPython source files retain their upstream copyright and license notices.
The upstream license is included as `data/sample/LICENSE`.

**Current scope:** the collected corpus is not yet indexed or connected to
`POST /chat`. Until retrieval and citations are implemented, LLM answers are
not source-verified. That work belongs to the next project phase.
