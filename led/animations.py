import time
import math
from typing import Tuple, List

class LEDAnimations:
    @staticmethod
    def rainbow_cycle(strip, wait_ms: int = 20):
        for j in range(256):
            for i in range(strip.numPixels()):
                color = LEDAnimations._wheel((int(i * 256 / strip.numPixels()) + j) & 255)
                strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)

    @staticmethod
    def _wheel(pos: int) -> int:
        if pos < 85:
            return LEDAnimations._color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return LEDAnimations._color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return LEDAnimations._color(0, pos * 3, 255 - pos * 3)

    @staticmethod
    def _color(red: int, green: int, blue: int) -> int:
        return (red << 16) | (green << 8) | blue

    @staticmethod
    def breathing_effect(strip, color: Tuple[int, int, int], cycles: int = 3):
        r, g, b = color
        for _ in range(cycles):
            for brightness in range(0, 256, 5):
                adjusted_color = LEDAnimations._color(
                    int(r * brightness / 255),
                    int(g * brightness / 255),
                    int(b * brightness / 255)
                )
                for i in range(strip.numPixels()):
                    strip.setPixelColor(i, adjusted_color)
                strip.show()
                time.sleep(0.02)

            for brightness in range(255, -1, -5):
                adjusted_color = LEDAnimations._color(
                    int(r * brightness / 255),
                    int(g * brightness / 255),
                    int(b * brightness / 255)
                )
                for i in range(strip.numPixels()):
                    strip.setPixelColor(i, adjusted_color)
                strip.show()
                time.sleep(0.02)