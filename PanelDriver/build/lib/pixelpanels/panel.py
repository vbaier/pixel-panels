import numpy as np

# This import and associated mock module is used to allow for running and debugging code
# on platforms for which rpi_ws281x cannot compile or execute
from typing import Tuple

try:
    from rpi_ws281x import PixelStrip
except ImportError:
    print("rpi_ws281x not on this system. Providing mock for testing.")
    from .mock_rpi_ws281x import PixelStrip


from enum import Enum, auto


class PanelOrigin(Enum):
    """Defines the location of the 0-index of the panel
    """
    BOTTOM_RIGHT = auto()
    BOTTOM_LEFT = auto()
    TOP_LEFT = auto()
    TOP_RIGHT = auto()


class PanelLayout(Enum):
    """Represents how pixels are indexed in a panel

    Layouts are determined by what the index of each LED is
    when the 0 index of the panel is in the top-left.

    VERTICAL_SNAKE = LED indices increase proceed along columns
    snaking back and forth like so
    -----------
    | 0  5  6 |
    | 1  4  7 |
    | 2  3  8 |
    -----------

    HORIZONTAL_SNAKE = LED indices increase proceed along rows
    snaking back and forth like so
    -----------
    | 0  1  2 |
    | 5  4  3 |
    | 6  7  8 |
    -----------
    """
    VERTICAL_SNAKE = auto()
    HORIZONTAL_SNAKE = auto()


class Panel(object):
    """Represents an individual RGB panel in a display.

    Args:
        pixel_width: The panel width in pixels
        pixel_height: The panel height in pixels
        layout: The index layout of the panel
        origin_location: The location of the 0-index of the panel
    """
    def __init__(self, pixel_width: int = 16, pixel_height: int = 16,
                 layout: PanelLayout = PanelLayout.VERTICAL_SNAKE,
                 origin_location: PanelOrigin = PanelOrigin.TOP_LEFT):

        self.__pixel_width = pixel_width
        self.__pixel_height = pixel_height
        self.__layout = layout
        self.__origin_location = origin_location
        self.__pixel_indices = self.__generate_indices()

    @property
    def pixel_width(self):
        """The width of the panel in pixels"""
        return self.__pixel_width

    @pixel_width.setter
    def pixel_width(self, value):
        self.__pixel_width = value
        self.__pixel_indices = self.__generate_indices()

    @property
    def pixel_height(self):
        """The height of the panel in pixels"""
        return self.__pixel_height

    @pixel_height.setter
    def pixel_height(self, value):
        self.__pixel_height = value
        self.__pixel_indices = self.__generate_indices()

    @property
    def layout(self):
        """The index layout of the panel"""
        return self.__layout

    @layout.setter
    def layout(self, value):
        self.__layout = value
        self.__pixel_indices = self.__generate_indices()

    @property
    def origin_location(self):
        """The location of the 0-index of the panel"""
        return self.__origin_location

    @origin_location.setter
    def origin_location(self, value):
        self.__origin_location = value
        self.__pixel_indices = self.__generate_indices()

    @property
    def pixel_indices(self):
        """A 2D-array (ndarray) of the form value[x_position,y_position]=led_index"""
        return self.__pixel_indices

    @property
    def pixel_count(self):
        """The number of pixels in this panel"""
        return self.pixel_width * self.pixel_height

    def __generate_indices(self):
        """Generates a mapping between the x,y indices of the panel and the pixel indices.
        """
        indices = np.zeros((self.pixel_width, self.pixel_height), int)

        if self.layout == PanelLayout.VERTICAL_SNAKE:
            indices = self.__generate_vertical_snake_indices()
        elif self.layout == PanelLayout.HORIZONTAL_SNAKE:
            indices = self.__generate_horizontal_snake_indices()

        indices = self.__map_indices_to_origin(indices)

        return indices

    def __generate_vertical_snake_indices(self):
        """Specialized index generator for the vertical_snake layout
        """
        indices = np.zeros((self.pixel_width, self.pixel_height), int)

        for x in range(self.pixel_width):
            for y in range(self.pixel_height):
                if x % 2 == 0:
                    indices[x][y] = x * self.pixel_height + y
                else:
                    indices[x][y] = (x + 1) * self.pixel_height - y - 1
        return indices

    # TODO: Add tests for panel. Especially horizontal snake which is not tested on hardware.
    def __generate_horizontal_snake_indices(self):
        """Specialized index generator for the horizontal_snake layout
        """
        indices = np.zeros((self.pixel_width, self.pixel_height), int)

        for y in range(self.pixel_height):
            for x in range(self.pixel_width):
                if y % 2 == 0:
                    indices[x][y] = y * self.pixel_width + x
                else:
                    indices[x][y] = (y + 1) * self.pixel_width - x - 1
        return indices

    def __map_indices_to_origin(self, indices):
        """Maps LED indices to a particular orientation of panel using its origin_location.
        """
        rotation_count = 0
        if self.origin_location == PanelOrigin.BOTTOM_LEFT:
            rotation_count = 1
        if self.origin_location == PanelOrigin.BOTTOM_RIGHT:
            rotation_count = 2
        if self.origin_location == PanelOrigin.TOP_RIGHT:
            rotation_count = 3

        return np.rot90(indices, rotation_count)


class PanelPlacement(object):
    """A panel support class that defines the placement of a panel in a panel display

    Args:
        panel: The panel being placed
        start_pixel: The pixel index of the first pixel in this panel
        end_pixel: The pixel index of the last pixel in this panel
    """
    def __init__(self, panel: Panel, start_pixel: Tuple[int, int] = (0, 0), end_pixel: Tuple[int, int] = (0, 0)):
        self.panel = panel
        self.start_pixel = start_pixel
        self.end_pixel = end_pixel
