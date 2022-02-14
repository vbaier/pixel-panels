class PixelStrip:
    """Mocked PixelStrip class that allows for developing on non-RPI platforms.
    """

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
        return self.__led_data
