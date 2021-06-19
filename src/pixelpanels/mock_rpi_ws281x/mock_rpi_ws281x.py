class PixelStrip:
    def __init__(self, num, pin, freq_hz=800000, dma=10, invert=False,
                 brightness=255, channel=0, strip_type=None, gamma=None):
        self.num = num
        self.__led_data = [0 for i in range(num)]

    def numPixels(self):
        return self.num

    def begin(self):
        return

    def setPixelColor(self, n, color):
        self.__led_data[n] = color
        return

    def getPixelColor(self, n):
        return self.__led_data[n]

    def show(self):
        return

    def getPixels(self):
        """Return an object which allows access to the LED display data as if
        it were a sequence of 24-bit RGB values.
        """
        return self.__led_data


def Color(red, green, blue, white=0):
    """Convert the provided red, green, blue color to a 24-bit color value.
    Each color component should be a value 0-255 where 0 is the lowest intensity
    and 255 is the highest intensity.
    """
    return (white << 24) | (red << 16) | (green << 8) | blue