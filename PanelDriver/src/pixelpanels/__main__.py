"""Pixelpanel Demo CLI

Provides a very simple demo CLI to test against the reference pixel panel electronics design. The CLI should be
called with a path to a gif and may include an option to provide a debug display.


This tool accepts comma separated value files (.csv) as well as excel
(.xls, .xlsx) files.

Example:
    Play a GIF indefinitely from the given path with the debug display

        $ python -m pixelpanels "../data/Example.gif" --debug

"""

import argparse
import sys

from matplotlib import pyplot

from pixelpanels import Display, PanelPlacement, Color
from pixelpanels.panel import PanelOrigin, Panel


def apply_color_cal(raw_color: Color) -> Color:
    """An example color calibration
    """

    calibrated_color = raw_color

    calibrated_color.red = int(calibrated_color.red * 0.40)
    calibrated_color.green = int(calibrated_color.green * 0.20)
    calibrated_color.blue = int(calibrated_color.blue * 0.45)

    return calibrated_color


def show_debug_image(image):
    """A simple debug display using matplotlib.pyplot
    """
    display_time = 0.001

    pyplot.clf()
    pyplot.imshow(image)
    pyplot.show(block=False)
    pyplot.pause(display_time)


def main() -> int:
    placements = [PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (0, 16), (15, 31)),
                  PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (16, 16), (31, 31)),
                  PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (32, 16), (47, 31)),
                  PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (48, 16), (63, 31)),
                  PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (0, 0), (15, 15)),
                  PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (16, 0), (31, 15)),
                  PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (32, 0), (47, 15)),
                  PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (48, 0), (63, 15))]

    parser = argparse.ArgumentParser()
    parser.add_argument("gif_path", help="Path to a gif you wish to display")
    parser.add_argument("--debug", help="Whether to activate the debug display window", action="store_true")
    parser.add_argument("--use_cal", help="Whether to use the default cal function", action="store_true")
    args = parser.parse_args()

    draw_callback = None
    if args.debug:
        draw_callback = show_debug_image

    display = Display(placements, draw_callback)

    if args.use_cal:
        display.color_cal = apply_color_cal

    try:
        while True:
            display.play_gif(args.gif_path)
    except KeyboardInterrupt:
        pass

    return 0


if __name__ == '__main__':
    sys.exit(main())
