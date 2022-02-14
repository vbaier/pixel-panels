from __future__ import print_function

import logging

import grpc
from pixelpanels.rpc_library import panelrpc_pb2, panelrpc_pb2_grpc


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = panelrpc_pb2_grpc.PanelControllerStub(channel)
        response = stub.PlayGif(panelrpc_pb2.PlayGifRequest(path='../data/local/NyanScaled.gif'))
    print("Gif status: " + response.message)


if __name__ == '__main__':
    logging.basicConfig()
    run()
