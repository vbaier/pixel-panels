import copy

from pixelpanels import Display
from pixelpanels.color import Color
from pixelpanels.panel import PanelOrigin, Panel, PanelPlacement

placements = [PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (0, 16), (15, 31)),
              PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (16, 16), (31, 31)),
              PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (32, 16), (47, 31)),
              PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (48, 16), (63, 31)),
              PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (0, 0), (15, 15)),
              PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (16, 0), (31, 15)),
              PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (32, 0), (47, 15)),
              PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (48, 0), (63, 15))]


def cal_function(raw_color):
    calibrated_color = copy.copy(raw_color)

    calibrated_color.red = raw_color.green
    calibrated_color.green = raw_color.blue
    calibrated_color.blue = raw_color.red

    return calibrated_color


def mock__draw(self):
    self.pixel_strip.show()

    if hasattr(self, 'image_history'):
        self.image_history.append(self.get_display_image())
    else:
        self.image_history = [self.get_display_image()]

    if self.debug_display:
        self.show_display_image(self.debug_display_time)


def mock_show(self):
    if hasattr(self, 'led_history'):
        self.led_history.append(copy.copy(self._PixelStrip__led_data))
    else:
        self.led_history = [copy.copy(self._PixelStrip__led_data)]
    return


def test_set_color():
    colors = [Color(0, 0, 0),
              Color(255, 0, 0),
              Color(0, 255, 0),
              Color(0, 0, 255),
              Color(255, 255, 255)]

    display = Display()

    for color in colors:
        display.set_color(color)

        for pixel_value in display.pixel_strip.getPixels():
            assert (pixel_value == color.to_pixel_value())


def test_calibration():
    colors = [Color(0, 0, 0),
              Color(255, 0, 0),
              Color(0, 255, 0),
              Color(0, 0, 255),
              Color(255, 255, 255)]

    display = Display()
    display.color_cal = cal_function

    for color in colors:
        display.set_color(color)

        for pixel_value in display.pixel_strip.getPixels():
            cal_color = Color(color.green, color.blue, color.red)
            assert (pixel_value == cal_color.to_pixel_value())


def test_horizontal_wipe(mocker):
    color = Color(255, 255, 255)
    wipe_speed = 2

    mocker.patch.object(Display, '_Display__draw', mock__draw)
    display = Display(placements)

    display.horizontal_wipe(color, 0)

    for frame_index, frame in enumerate(display.image_history):
        wipe_end = (frame_index + 1) * wipe_speed
        for x in range(display.pixel_width):
            for y in range(display.pixel_height):
                if x < wipe_end:
                    assert (frame.getpixel((x, y)) == color.to_tuple())
                else:
                    assert (frame.getpixel((x, y)) == (0, 0, 0))


def test_vertical_wipe(mocker):
    color = Color(255, 255, 255)
    wipe_speed = 2

    mocker.patch.object(Display, '_Display__draw', mock__draw)
    display = Display(placements)

    display.vertical_wipe(color, 0)

    for frame_index, frame in enumerate(display.image_history):
        wipe_end = (frame_index + 1) * wipe_speed
        for x in range(display.pixel_width):
            for y in range(display.pixel_height):
                if y < wipe_end:
                    assert (frame.getpixel((x, y)) == color.to_tuple())
                else:
                    assert (frame.getpixel((x, y)) == (0, 0, 0))


def test_pixel_wipe(mocker):
    color = Color(255, 255, 255)

    mocker.patch.object(Display, '_Display__draw', mock__draw)
    display = Display(placements)

    display.pixel_wipe(color, 0)

    for frame_index, frame in enumerate(display.image_history):

        for y in range(display.pixel_height):
            for x in range(display.pixel_width):
                wipe_end = frame_index+1 - y*display.pixel_width
                if x < wipe_end:
                    assert (frame.getpixel((x, y)) == color.to_tuple())
                else:
                    assert (frame.getpixel((x, y)) == (0, 0, 0))


def test_show_image(mocker):
    image_path = "./data/Test1_64x32.png"

    mocker.patch.object(Display, '_Display__draw', mock__draw)
    display = Display(placements)

    display.set_image(image_path)
    # TODO: Add assertions


def test_play_gif(mocker):
    image_path = "./data/Test_64x32.gif"

    mocker.patch.object(Display, '_Display__draw', mock__draw)
    display = Display(placements)

    display.play_gif(image_path)
    # TODO: Add assertions
