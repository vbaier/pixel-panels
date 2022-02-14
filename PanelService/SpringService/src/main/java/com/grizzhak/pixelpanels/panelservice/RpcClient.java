package com.grizzhak.pixelpanels.panelservice;

import java.util.logging.Level;
import java.util.logging.Logger;

import com.grizzhak.pixelpanels.PanelControllerGrpc;
import com.grizzhak.pixelpanels.PlayGifRequest;
import com.grizzhak.pixelpanels.PlayGifResponse;
import io.grpc.Channel;
import io.grpc.StatusRuntimeException;

public class RpcClient {
    private static final Logger logger = Logger.getLogger(RpcClient.class.getName());

    private final PanelControllerGrpc.PanelControllerBlockingStub blockingStub;

    public RpcClient(Channel channel) {
        // 'channel' here is a Channel, not a ManagedChannel, so it is not this code's responsibility to
        // shut it down.

        // Passing Channels to code makes code easier to test and makes it easier to reuse Channels.
        blockingStub = PanelControllerGrpc.newBlockingStub(channel);
    }

    public void RunClient() {

        final PlayGifRequest request = PlayGifRequest.newBuilder().setPath("../data/Test_64x32.gif").build();
        PlayGifResponse response = null;
        try {
            response = blockingStub.playGif(request);
        } catch (final StatusRuntimeException e) {
            logger.log(Level.WARNING, "RPC failed: {0}", e.getStatus());
        }
        finally {
            logger.log(Level.INFO, "Response: {0}", response);
        }
    }
}
