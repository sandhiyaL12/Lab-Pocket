# Ten lab questions

MicroPython documentation is maintained as source files, not paginated PDFs.
References below identify the source file and relevant API/port section.

| # | Question | Source file(s) / section(s) | Needs more than one page? |
|---|---|---|---|
| 1 | How do I configure an ESP32 pin as an output and read its value? | `data/raw/docs/library/machine.Pin.rst` (Pin API); `data/raw/docs/esp32/quickref.rst` (ESP32 pins); `data/raw/ports/esp32/machine_pin.c` | Yes |
| 2 | Does the ESP32 `machine.Pin` implementation support pull-ups and open-drain output, and are all GPIOs interchangeable? | `data/raw/docs/library/machine.Pin.rst`; `data/raw/docs/esp32/quickref.rst`; `data/raw/ports/esp32/machine_pin.c` | Yes |
| 3 | Does hardware PWM work on every Pico GPIO, and how do I set its frequency and duty cycle? | `data/raw/docs/library/machine.PWM.rst`; `data/raw/docs/rp2/quickref.rst` (PWM); `data/raw/ports/rp2/machine_pwm.c` | Yes |
| 4 | Is RP2 I2C implemented using hardware or software, and how do I choose its pins and frequency? | `data/raw/docs/library/machine.I2C.rst`; `data/raw/docs/rp2/quickref.rst` (I2C); `data/raw/ports/rp2/machine_i2c.c` | Yes |
| 5 | How do I scan an I2C bus on ESP32 and choose SCL/SDA pins? | `data/raw/docs/library/machine.I2C.rst`; `data/raw/docs/esp32/quickref.rst` (I2C); `data/raw/ports/esp32/machine_i2c.c` | Yes |
| 6 | What ADC range and resolution should I expect on ESP32 versus Pico? | `data/raw/docs/library/machine.ADC.rst`; `data/raw/docs/esp32/quickref.rst` (ADC); `data/raw/docs/rp2/quickref.rst` (ADC) | Yes |
| 7 | How do I connect an ESP32 to Wi-Fi in station mode and check whether it connected? | `data/raw/docs/library/network.WLAN.rst`; `data/raw/docs/esp32/quickref.rst` (network); `data/raw/ports/esp32/network_wlan.c` | Yes |
| 8 | Where is garbage collection implemented, how can I check free memory, and what determines ESP32 heap capacity? | `data/raw/docs/library/gc.rst`; `data/raw/py/gc.c`; `data/raw/ports/esp32/gccollect.c`; ESP32 startup/configuration files | Yes |
| 9 | How can I use RP2 PIO to generate a custom signal, and what are the state-machine limits? | `data/raw/docs/library/rp2.PIO.rst`; `data/raw/docs/rp2/quickref.rst` (PIO); `data/raw/ports/rp2/rp2_pio.c` | Yes |
| 10 | Is the GPIO pin on the Pico board at my lab bench physically damaged? | Cannot be determined from MicroPython source or documentation; the board must be tested. | No |
