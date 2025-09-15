import time
import threading
from typing import Tuple, Optional
from config.settings import Settings
from config.family_names import FAMILY_MEMBERS, LED_POSITIONS

try:
    if not Settings.MOCK_MODE:
        from rpi_ws281x import PixelStrip, Color
except ImportError:
    pass

class MockPixelStrip:
    def __init__(self, led_count, led_pin, led_freq_hz, led_dma, led_invert, led_brightness, led_channel):
        self.led_count = led_count
        self.pixels = [(0, 0, 0)] * led_count
        self.brightness = led_brightness

    def begin(self):
        print("Mock LED Strip initialized")

    def setPixelColor(self, n, color):
        if 0 <= n < self.led_count:
            if isinstance(color, int):
                r = (color >> 16) & 0xff
                g = (color >> 8) & 0xff
                b = color & 0xff
                self.pixels[n] = (r, g, b)
            else:
                self.pixels[n] = color

    def show(self):
        pass

    def setBrightness(self, brightness):
        self.brightness = brightness

class LEDController:
    def __init__(self):
        self.strip = None
        self.animation_thread = None
        self.animation_running = False
        self.animation_lock = threading.Lock()
        self.initialize_strip()

    def initialize_strip(self):
        if Settings.MOCK_MODE:
            self.strip = MockPixelStrip(
                Settings.LED_COUNT,
                Settings.LED_PIN,
                Settings.LED_FREQ_HZ,
                Settings.LED_DMA,
                Settings.LED_INVERT,
                Settings.LED_BRIGHTNESS,
                Settings.LED_CHANNEL
            )
        else:
            self.strip = PixelStrip(
                Settings.LED_COUNT,
                Settings.LED_PIN,
                Settings.LED_FREQ_HZ,
                Settings.LED_DMA,
                Settings.LED_INVERT,
                Settings.LED_BRIGHTNESS,
                Settings.LED_CHANNEL
            )

        self.strip.begin()

    def stop_animation(self):
        with self.animation_lock:
            self.animation_running = False
        if self.animation_thread and self.animation_thread.is_alive():
            self.animation_thread.join()

    def clear_all(self):
        self.stop_animation()
        for i in range(Settings.LED_COUNT):
            self.strip.setPixelColor(i, 0)
        self.strip.show()
        if Settings.MOCK_MODE:
            print("LED: All cleared")

    def set_color(self, start: int, end: int, color: Tuple[int, int, int]):
        r, g, b = color
        color_value = (r << 16) | (g << 8) | b
        for i in range(start, min(end, Settings.LED_COUNT)):
            self.strip.setPixelColor(i, color_value)
        self.strip.show()

    def illuminate_family_member(self, name: str, color: Tuple[int, int, int] = (255, 255, 255)):
        name = name.upper()
        if name in LED_POSITIONS:
            start, end = LED_POSITIONS[name]
            self.clear_all()
            self.set_color(start, end, color)
            if Settings.MOCK_MODE:
                print(f"LED: Illuminating {name} with color {color}")

    def set_listening_mode(self):
        self.stop_animation()
        self.animation_running = True
        self.animation_thread = threading.Thread(target=self._pulse_blue)
        self.animation_thread.start()

    def set_recording_mode(self):
        self.stop_animation()
        self.set_color(0, Settings.LED_COUNT, (255, 0, 0))
        if Settings.MOCK_MODE:
            print("LED: Recording mode - Red")

    def set_idle_mode(self):
        self.stop_animation()
        self.animation_running = True
        self.animation_thread = threading.Thread(target=self._cycle_family_names)
        self.animation_thread.start()

    def _pulse_blue(self):
        while self.animation_running:
            for brightness in range(0, 256, 5):
                if not self.animation_running:
                    break
                self.set_color(0, Settings.LED_COUNT, (0, 0, brightness))
                time.sleep(0.02)

            for brightness in range(255, -1, -5):
                if not self.animation_running:
                    break
                self.set_color(0, Settings.LED_COUNT, (0, 0, brightness))
                time.sleep(0.02)

    def _cycle_family_names(self):
        colors = [
            (255, 100, 100),  # Red
            (100, 255, 100),  # Green
            (100, 100, 255),  # Blue
            (255, 255, 100),  # Yellow
            (255, 100, 255),  # Magenta
            (100, 255, 255),  # Cyan
        ]

        color_index = 0
        member_index = 0

        while self.animation_running:
            if FAMILY_MEMBERS:
                name = FAMILY_MEMBERS[member_index]
                color = colors[color_index]

                if name in LED_POSITIONS:
                    start, end = LED_POSITIONS[name]
                    self.clear_all()
                    self.set_color(start, end, color)

                    if Settings.MOCK_MODE:
                        print(f"LED: Cycling - {name} with color {color}")

                member_index = (member_index + 1) % len(FAMILY_MEMBERS)
                if member_index == 0:
                    color_index = (color_index + 1) % len(colors)

            time.sleep(2.0)