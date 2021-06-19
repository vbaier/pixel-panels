import argparse
import sys

from pixelpanels import Display, PanelPlacement
from pixelpanels.panel import PanelOrigin, Panel


def apply_color_cal(raw_color):

    calibrated_color = raw_color

    calibrated_color.red = int(calibrated_color.red*0.40)
    calibrated_color.green = int(calibrated_color.green*0.20)
    calibrated_color.blue = int(calibrated_color.blue*0.45)

    return calibrated_color


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
    args = parser.parse_args()

    display = Display(placements, args.debug, 0.01)
    display.color_cal = apply_color_cal

    try:
        while True:
            display.play_gif(args.gif_path)
    except KeyboardInterrupt:
        pass

    return 0


if __name__ == '__main__':
    sys.exit(main())
