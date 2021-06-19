class Color:
    def __init__(self, red=0, green=0, blue=0):
        self.red = red
        self.green = green
        self.blue = blue

    @staticmethod
    def from_pixel_value(pixel_value):
        return Color((pixel_value & 0xFF0000) >> 16,
                     (pixel_value & 0x00FF00) >> 8,
                     (pixel_value & 0x0000FF) >> 0)

    @staticmethod
    def from_tuple(color_tuple):
        return Color(color_tuple[0],
                     color_tuple[1],
                     color_tuple[2])

    def to_pixel_value(self):
        return (self.red << 16) | (self.green << 8) | (self.blue << 0)

    def to_tuple(self):
        return self.red, self.green, self.blue
