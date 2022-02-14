package com.grizzhak.pixelpanels.panelservice;

import java.io.File;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

import io.grpc.Grpc;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.TlsChannelCredentials;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;
import org.springframework.hateoas.CollectionModel;
import org.springframework.hateoas.EntityModel;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import static org.springframework.hateoas.server.mvc.WebMvcLinkBuilder.*;

@RestController
public class PanelController {

    private final PanelRepository repository;

    @Value("${pixelpanels.certificates.rootCaCert}")
    private Resource rootCa;

    @Value("${pixelpanels.certificates.clientCert}")
    private Resource clientCert;

    @Value("${pixelpanels.certificates.clientKey}")
    private Resource clientKey;

    PanelController(PanelRepository repository) {
        this.repository = repository;
    }

    @GetMapping("/PlayGif")
    @ResponseStatus(value = HttpStatus.OK)
    public void playGif() throws Exception{

        String target = "localhost:50051";

        TlsChannelCredentials.Builder tlsBuilder = TlsChannelCredentials.newBuilder()
                .keyManager(clientCert.getFile(), clientKey.getFile())
                .trustManager(rootCa.getFile());

        ManagedChannel channel = channel = Grpc.newChannelBuilder(target, tlsBuilder.build())
                .build();

        //RpcClient
        try {
            RpcClient client = new RpcClient(channel);
            client.RunClient();
        } finally {
            // ManagedChannels use resources like threads and TCP connections. To prevent leaking these
            // resources the channel should be shut down when it will no longer be used. If it may be used
            // again leave it running.
            channel.shutdownNow().awaitTermination(30, TimeUnit.SECONDS);
        }
    }

    // Aggregate root
    // tag::get-aggregate-root[]
    @GetMapping("/Panels")
    CollectionModel<EntityModel<Panel>> all() {

        List<EntityModel<Panel>> Panels = repository.findAll().stream()
                .map(Panel -> EntityModel.of(Panel,
                        linkTo(methodOn(PanelController.class).one(Panel.getId())).withSelfRel(),
                        linkTo(methodOn(PanelController.class).all()).withRel("Panels")))
                .collect(Collectors.toList());

        return CollectionModel.of(Panels, linkTo(methodOn(PanelController.class).all()).withSelfRel());
    }
    // end::get-aggregate-root[]

    @PostMapping("/Panels")
    Panel newPanel(@RequestBody Panel newPanel) {
        return repository.save(newPanel);
    }

    // Single item

    @GetMapping("/Panels/{id}")
    EntityModel<Panel> one(@PathVariable Long id) {

        Panel Panel = repository.findById(id) //
                .orElseThrow(() -> new PanelNotFoundException(id));

        return EntityModel.of(Panel, //
                linkTo(methodOn(PanelController.class).one(id)).withSelfRel(),
                linkTo(methodOn(PanelController.class).all()).withRel("Panels"));
    }

    @PutMapping("/Panels/{id}")
    Panel replacePanel(@RequestBody Panel newPanel, @PathVariable Long id) {

        return repository.findById(id)
                .map(Panel -> {
                    Panel.setImagePath(newPanel.getImagePath());
                    return repository.save(Panel);
                })
                .orElseGet(() -> {
                    newPanel.setId(id);
                    return repository.save(newPanel);
                });
    }

    @DeleteMapping("/Panels/{id}")
    void deletePanel(@PathVariable Long id) {
        repository.deleteById(id);
    }
}
