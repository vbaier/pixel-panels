"""Pixelpanel Demo RPC Server

Provides a very simple demo RPC Server to test against the reference pixel
panel electronics design. The server exposes a single handler for playing
a GIF from a path local to the server.

Attributes:
    panel_display (Display): A process-global variable used to hold the display
    being used by the worker threads on the server

    image_queue (Queue): A process-global queue used to pass images from the
    worker threads to the main thread for display. Pyplot is not thread safe
    and must be run on the main thread so we require this queue mechanism
    to manage that lack of thread safety
"""
import argparse
import sys
from concurrent import futures
import logging
from queue import Queue

import grpc
import matplotlib.pyplot as pyplot

from pixelpanels import PanelPlacement, Panel, Display, Color
from pixelpanels.panel import PanelOrigin
from pixelpanels.rpc_library import panelrpc_pb2_grpc, panelrpc_pb2

panel_display = None
image_queue = Queue()


def show_debug_image(display_time=0.001):
    """A simple debug display call using matplotlib.pyplot
    """
    global image_queue

    display_time = 0.001

    while not image_queue.empty():
        image = image_queue.get()

        pyplot.clf()
        pyplot.imshow(image)
        pyplot.show(block=False)
        pyplot.pause(display_time)


def apply_color_cal(raw_color: Color) -> Color:
    """An example color calibration
    """

    calibrated_color = raw_color

    calibrated_color.red = int(calibrated_color.red * 0.40)
    calibrated_color.green = int(calibrated_color.green * 0.20)
    calibrated_color.blue = int(calibrated_color.blue * 0.45)

    return calibrated_color


def push_image_to_display_queue(image):
    """A draw callback that will be used by workers to pass images to the debug display
    """
    global image_queue

    image_queue.put(image)


def get_panel_display():
    """A module-level method to provide access to a single instance of the panel display
    """
    global panel_display

    if panel_display is None:
        placements = [PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (0, 16), (15, 31)),
                      PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (16, 16), (31, 31)),
                      PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (32, 16), (47, 31)),
                      PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (48, 16), (63, 31)),
                      PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (0, 0), (15, 15)),
                      PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (16, 0), (31, 15)),
                      PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (32, 0), (47, 15)),
                      PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (48, 0), (63, 15))]

        panel_display = Display(placements, push_image_to_display_queue)

    return panel_display


def play_gif(gif_path):
    """The handler for the play_gif request
    """
    display = get_panel_display()

    result_msg = "GIF Playback Failed"
    try:
        display.play_gif(gif_path)
        result_msg = "Play Successful!"
    except Exception:
        logging.warning("GIF playback was unsuccessful with path: {0}".format(gif_path))
        raise

    return result_msg


class PanelController(panelrpc_pb2_grpc.PanelControllerServicer):
    """A controller to handle incoming requests
    """

    def PlayGif(self, request, context):
        result_msg = play_gif(request.path)
        return panelrpc_pb2.PlayGifResponse(message=result_msg)


def serve():
    """Starts the server and enters a main loop that splits time between the server processing messages and
    the debug display showing resulting images.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    panelrpc_pb2_grpc.add_PanelControllerServicer_to_server(PanelController(), server)
    with open('./certificates/server_nopass.key', 'rb') as f:
        server_key = f.read()
    with open('./certificates/server.crt', 'rb') as f:
        server_cert = f.read()
    with open('./certificates/rootCA.crt', 'rb') as f:
        root_ca_cert = f.read()
    server_credentials = grpc.ssl_server_credentials([(server_key, server_cert)], root_ca_cert, True)

    server.add_secure_port('localhost:50051', server_credentials)
    # server.add_insecure_port('[::]:50051')
    server.start()

    while server.wait_for_termination(0.1):
        show_debug_image()


def main() -> int:
    logging.basicConfig()

    placements = [PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (0, 16), (15, 31)),
                  PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (16, 16), (31, 31)),
                  PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (32, 16), (47, 31)),
                  PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (48, 16), (63, 31)),
                  PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (0, 0), (15, 15)),
                  PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (16, 0), (31, 15)),
                  PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (32, 0), (47, 15)),
                  PanelPlacement(Panel(origin_location=PanelOrigin.TOP_LEFT), (48, 0), (63, 15))]

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="Whether to activate the debug display window", action="store_true")
    parser.add_argument("--use_cal", help="Whether to use the default cal function", action="store_true")
    args = parser.parse_args()

    draw_callback = None
    if args.debug:
        draw_callback = show_debug_image

    display = Display(placements, draw_callback)

    if args.use_cal:
        display.color_cal = apply_color_cal
    serve()


if __name__ == '__main__':
    sys.exit(main())
