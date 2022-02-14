from typing import Tuple


class Color:
    """Simple support class for translating different 24-bit RGB color formats.

    Args:
        red: byte-value of the red channel from 0-255
        green: byte-value of the red channel from 0-255
        blue: byte-value of the red channel from 0-255
    """

    def __init__(self, red: int = 0, green: int = 0, blue: int = 0):
        self.red = red
        self.green = green
        self.blue = blue

    @staticmethod
    def from_pixel_value(pixel_value: int) -> 'Color':
        """Creates a `Color` from a 24-bit packed integer

        This is primarily used in the context of converting pixel values that
        are clocked out directly to the hardware into our Color utility class.

        Args:
            pixel_value: A 24-bit integer of the format (red << 16) |
            (green << 8) | (blue << 0)

        Returns:
            A new Color instance
        """
        return Color((pixel_value & 0xFF0000) >> 16,
                     (pixel_value & 0x00FF00) >> 8,
                     (pixel_value & 0x0000FF) >> 0)

    @staticmethod
    def from_tuple(color_tuple: Tuple[int, int, int]) -> 'Color':
        """Creates a `Color` from a tuple representing RGB values

        Args:
            color_tuple: A tuple of the form (red, green, blue)

        Returns:
            A new Color instance
        """
        return Color(color_tuple[0],
                     color_tuple[1],
                     color_tuple[2])

    def to_pixel_value(self) -> int:
        """Converts this 'Color' to a 24-bit packed integer

        Returns:
            A 24-bit integer of the format (red << 16) | (green << 8) | (blue << 0)
        """
        return (self.red << 16) | (self.green << 8) | (self.blue << 0)

    def to_tuple(self) -> Tuple[int, int, int]:
        """Converts this 'Color' to a tuple representing RGB values

        Returns:
            A tuple of the form (red, green, blue)
        """
        return self.red, self.green, self.blue
