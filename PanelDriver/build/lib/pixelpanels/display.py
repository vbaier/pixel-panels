import copy
import time
from threading import Lock
from typing import List, Callable

# We must alias the module separately so that type hinting works
from PIL import Image as ImageLib
from PIL.Image import Image

from .color import Color
from .panel import PanelOrigin, Panel, PanelPlacement

# This import and associated mock module is used to allow for running and debugging code
# on platforms for which rpi_ws281x cannot compile or execute
try:
    from rpi_ws281x import PixelStrip
except ImportError:
    print("rpi_ws281x not on this system. Providing mock for testing.")
    from .mock_rpi_ws281x import PixelStrip


class Display(object):
    """Represents a pixel display made up of several panels

    Note:
        Placements must be listed in order of how they are connected to ensure the
        LED data is clocked out properly

    Args:
        placements: A list of PanelPlacement objects in order of their connection. By
        default, this will be a 64x32 display made of 8 panels.

        draw_callback: A function that is called with a PIL Image as an argument whenever
        the panel is drawn to. This can be useful for debugging or otherwise monitoring what is
        being sent to the display

        color_cal: A function that takes a Color and transforms it into another Color. Called
        before each pixel color is set to provide arbitrary color calibration.
    """
    def __init__(self, placements: List[PanelPlacement] = None,
                 draw_callback: Callable[[Image], None] = None,
                 color_cal: Callable[[Color], Color] = None):

        if placements is None:
            # Create a default 2x4 panel placement
            placements = [PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (0, 16), (15, 31)),
                          PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (16, 16), (31, 31)),
                          PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (32, 16), (47, 31)),
                          PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (48, 16), (63, 31)),
                          PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (0, 0), (15, 15)),
                          PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (16, 0), (31, 15)),
                          PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (32, 0), (47, 15)),
                          PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (48, 0), (63, 15))]

        self.__placements = placements
        self.__regenerate_pixel_indices()

        self.__draw_lock = Lock()
        self.__draw_callback = draw_callback

        # TODO: extract these into a settings class
        LED_COUNT = self.__pixel_count  # Number of LED pixels.
        LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
        LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
        LED_DMA = 10  # DMA channel to use for generating signal (try 10)
        LED_BRIGHTNESS = 16  # Set to 0 for darkest and 255 for brightest
        LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
        LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53

        self.pixel_strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)

        # Intialize the pixel strip library. This must be called before pixel_strip is otherwise used
        self.pixel_strip.begin()

        self.color_cal = color_cal

    def __regenerate_pixel_indices(self):
        """Recalculates the mapping between the (x,y) index in the display and the linear index
        in the pixel strip.
        """

        led_index_offset = 0
        display_index_dict = {}

        for placement in self.placements:
            for x in range(placement.panel.pixel_width):
                for y in range(placement.panel.pixel_height):
                    display_index_dict[(x + placement.start_pixel[0],
                                        y + placement.start_pixel[1])] = \
                        placement.panel.pixel_indices[x, y] + led_index_offset
            led_index_offset += placement.panel.pixel_width * placement.panel.pixel_height

        # Extract key variables from the dictionary
        self.__pixel_count = len(display_index_dict)
        self.__pixel_width = max(display_index_dict.keys(), key=lambda pixel: pixel[0])[0] + 1
        self.__pixel_height = max(display_index_dict.keys(), key=lambda pixel: pixel[1])[1] + 1

        # We convert the dictionary to a 2d list for a couple of reasons. First, it makes lookup
        # very quick which is better since it will be done real-time. Second, we must explicitly
        # convert our earlier numpy integer elements to plain Python integers or our lower-level
        # LED driver code will complain
        self.__pixel_indices = [[int(display_index_dict[(x, y)]) for y in range(self.__pixel_height)] for x in
                                range(self.__pixel_width)]

    def __set_pixel_color(self, x, y, color):

        cal_color = copy.copy(color)

        if self.color_cal is not None:
            cal_color = self.color_cal(cal_color)

        pixel_value = cal_color.to_pixel_value()
        self.pixel_strip.setPixelColor(self.__pixel_indices[x][y], pixel_value)

    def __fit_image_to_panel(self, src_image):

        resized_image = src_image.resize((self.__pixel_width, self.__pixel_height), ImageLib.LANCZOS)
        return resized_image

    def __draw(self):

        self.__draw_lock.acquire()

        self.pixel_strip.show()
        if self.__draw_callback is not None:
            self.__draw_callback(self.get_display_image())
        self.__draw_lock.release()

    @property
    def placements(self):

        return self.__placements

    @placements.setter
    def placements(self, value):

        self.__placements = value
        self.__regenerate_pixel_indices()

    @property
    def pixel_count(self):
        return self.__pixel_count

    @property
    def pixel_width(self):
        return self.__pixel_width

    @property
    def pixel_height(self):
        return self.__pixel_height

    def print_indices(self):
        print(self.__pixel_indices)

    def set_color(self, color):
        for x in range(self.__pixel_width):
            for y in range(self.__pixel_height):
                self.__set_pixel_color(x, y, color)

        self.__draw()

    def get_display_image(self):
        """Gets the currently displayed pixel data as an image

        Returns:
            A PIL Image matching what is currently stored in the display
        """
        image = ImageLib.new("RGB", (self.__pixel_width, self.__pixel_height))
        rgb_data = [0] * (self.__pixel_width*self.__pixel_height)

        for y in range(self.__pixel_height):
            for x in range(self.__pixel_width):
                pixel_value = self.pixel_strip.getPixelColor(self.__pixel_indices[x][y])
                pixel_color = Color.from_pixel_value(pixel_value)
                i = y*self.__pixel_width + x
                rgb_data[i] = pixel_color.to_tuple()

        image.putdata(rgb_data)
        return image

    def horizontal_wipe(self, color: Color, delay_ms: int = 50):
        """Performs a horizontal color wipe across the display

        Args:
            color: The color to display
            delay_ms: The number of milliseconds to wait between
            frames of animation

        Todo:
            * Extract the modulus parameter into an argument so
            that the number of lines drawn for each frame in the
            wipe is controlled by the caller
        """
        for x in range(self.__pixel_width):

            for y in range(self.__pixel_height):
                self.__set_pixel_color(x, y, color)

            if (x + 1) % 2 == 0:
                time.sleep(delay_ms / 1000.0)
                self.__draw()

    def vertical_wipe(self, color: Color, delay_ms: int = 50):
        """Performs a vertical color wipe across the display

        Args:
            color: The color to display
            delay_ms: The number of milliseconds to wait between
            frames of animation

        Todo:
            * Extract the modulus parameter into an argument so
            that the number of lines drawn for each frame in the
            wipe is controlled by the caller
        """
        for y in range(self.__pixel_height):

            for x in range(self.__pixel_width):
                self.__set_pixel_color(x, y, color)

            if (y + 1) % 2 == 0:
                time.sleep(delay_ms / 1000.0)
                self.__draw()

    def pixel_wipe(self, color, delay_ms=1):
        """Performs a color wipe in order of the pixel indices

        Args:
            color: The color to display
            delay_ms: The number of milliseconds to wait between
            frames of animation

        Todo:
            * Add a modulus parameter as an argument so
            that the number of pixels drawn for each frame in the
            wipe is controlled by the caller
        """
        for y in range(self.__pixel_height):

            for x in range(self.__pixel_width):
                self.__set_pixel_color(x, y, color)
                time.sleep(delay_ms / 1000.0)
                self.__draw()

    def set_image(self, path: str):
        """Displays an image file on the pixel display

        Args:
            path: The path to the image that will be displayed

        Todo:
            * Refactor this to simply take a PIL Image and
            leave the caller to do any opening of files or
            creation of image data
        """
        with Image.open(path) as image:

            image_width, image_height = image.size

            for y in range(self.__pixel_height):

                if y >= image_height:
                    continue

                for x in range(self.__pixel_width):

                    if x >= image_width:
                        continue

                    pixel_color = image.getpixel((x, y))
                    self.__set_pixel_color(x, y, Color(pixel_color[0],
                                                       pixel_color[1],
                                                       pixel_color[2]))

            self.__draw()

    def play_gif(self, path):
        """Plays a GIF from the file path provided

        Args:
            path: The path to the GIF that will be displayed

        Todo:
            * Refactor this to simply take a PIL Image and
            leave the caller to do any opening of files or
            creation of image data
        """
        with ImageLib.open(path) as image:

            frame_count = getattr(image, "n_frames", 1)

            if frame_count == 1:
                return

            for i in range(frame_count):

                image.seek(i)
                frame = image.convert('RGB')
                resized = self.__fit_image_to_panel(frame)

                for y in range(self.__pixel_height):
                    for x in range(self.__pixel_width):
                        pixel_color = resized.getpixel((x, y))
                        self.__set_pixel_color(x, y, Color.from_tuple(pixel_color))

                self.__draw()
