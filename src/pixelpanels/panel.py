# Library for manipulating pixel panels
# Author: Vincent Baier

# Provide a switch for testing on windows and other locations where
# the ws281x library won't compile. Since the module doesn't exist
# at all, we can't just mock it in the unit test.

import numpy as np

try:
    from rpi_ws281x import PixelStrip
except ImportError:
    print("rpi_ws281x not on this system. Providing mock for testing.")
    from .mock_rpi_ws281x import PixelStrip

from enum import Enum, auto


class PanelOrigin(Enum):
    """
    Defines the location of the 0-index of the panel
    """
    BOTTOM_RIGHT = auto()
    BOTTOM_LEFT = auto()
    TOP_LEFT = auto()
    TOP_RIGHT = auto()


class PanelLayout(Enum):
    """
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

    def __init__(self, pixel_width=16, pixel_height=16,
                 pixel_layout=PanelLayout.VERTICAL_SNAKE,
                 origin_location=PanelOrigin.TOP_LEFT):

        self.__pixel_width = pixel_width
        self.__pixel_height = pixel_height
        self.__pixel_layout = pixel_layout
        self.__origin_location = origin_location
        self.__pixel_indices = self.__generate_indices()

    @property
    def pixel_width(self):
        return self.__pixel_width

    @pixel_width.setter
    def pixel_width(self, value):
        self.__pixel_width = value
        self.__pixel_indices = self.__generate_indices()

    @property
    def pixel_height(self):
        return self.__pixel_height

    @pixel_height.setter
    def pixel_height(self, value):
        self.__pixel_height = value
        self.__pixel_indices = self.__generate_indices()

    @property
    def pixel_layout(self):
        return self.__pixel_layout

    @pixel_layout.setter
    def pixel_layout(self, value):
        self.__pixel_layout = value
        self.__pixel_indices = self.__generate_indices()

    @property
    def origin_location(self):
        return self.__origin_location

    @origin_location.setter
    def origin_location(self, value):
        self.__origin_location = value
        self.__pixel_indices = self.__generate_indices()

    @property
    def pixel_indices(self):
        return self.__pixel_indices

    @property
    def pixel_count(self):
        return self.pixel_width * self.pixel_height

    def __generate_indices(self):

        indices = np.zeros((self.pixel_width, self.pixel_height), int)

        if self.pixel_layout == PanelLayout.VERTICAL_SNAKE:
            indices = self.__generate_vertical_snake_indices()
        elif self.pixel_layout == PanelLayout.HORIZONTAL_SNAKE:
            indices = self.__generate_horizontal_snake_indices()

        indices = self.__map_indices_to_origin(indices)

        return indices

    def __generate_vertical_snake_indices(self):

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

        indices = np.zeros((self.pixel_width, self.pixel_height), int)

        for y in range(self.pixel_height):
            for x in range(self.pixel_width):
                if y % 2 == 0:
                    indices[x][y] = y * self.pixel_width + x
                else:
                    indices[x][y] = (y + 1) * self.pixel_width - x - 1
        return indices

    def __map_indices_to_origin(self, indices):
        """
        Maps LED indices to a particular orientation of panel using
        OriginLocation.

        :param indices:
        Un-mapped LED indices
        :return:
        LED indices mapped to the current OriginLocation
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
    def __init__(self, panel: Panel, start_pixel=(0, 0), end_pixel=(0, 0)):
        self.panel = panel
        self.start_pixel = start_pixel
        self.end_pixel = end_pixel
