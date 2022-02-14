package com.grizzhak.pixelpanels.panelservice;

import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.hateoas.CollectionModel;
import org.springframework.hateoas.EntityModel;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import javax.servlet.http.HttpServletRequest;

import static org.springframework.hateoas.server.mvc.WebMvcLinkBuilder.*;

@RestController
public class ImageController {

    @Autowired
    ImageStorageService imageStorageService;;

    // Aggregate root
    // tag::get-aggregate-root[]
    @GetMapping("/image")
    CollectionModel<EntityModel<Image>> all() {

        List<EntityModel<Image>> Images = imageStorageService.imageMetadataRepository.findAll().stream()
                .map(Image -> EntityModel.of(Image,
                        linkTo(methodOn(ImageController.class).one(Image.getId())).withSelfRel(),
                        linkTo(methodOn(ImageController.class).all()).withRel("image")))
                .collect(Collectors.toList());

        return CollectionModel.of(Images, linkTo(methodOn(ImageController.class).all()).withSelfRel());
    }
    // end::get-aggregate-root[]

    @PostMapping("/image")
    Long uploadImage(@RequestParam MultipartFile image) throws Exception {
        return imageStorageService.save(image.getBytes(), image.getOriginalFilename());
    }

    @GetMapping("/image/{id}")
    EntityModel<Image> one(@PathVariable Long id) {

        Image Image = imageStorageService.imageMetadataRepository.findById(id) //
                .orElseThrow(() -> new PanelNotFoundException(id));

        return EntityModel.of(Image, //
                linkTo(methodOn(ImageController.class).one(id)).withSelfRel(),
                linkTo(methodOn(ImageController.class).all()).withRel("image"));
    }

    @PutMapping("/image/{id}")
    Long replaceImage(@RequestParam MultipartFile newImage) {
        throw new UnsupportedOperationException();
    }

    @DeleteMapping("/image/{id}")
    void deletePanel(@PathVariable Long id) {
        throw new UnsupportedOperationException();
    }

    @GetMapping("/image/download/{id}")
    public ResponseEntity<Resource> downloadImage(@PathVariable Long id, HttpServletRequest request) {
        // Load file as Resource
        Resource resource = imageStorageService.find(id);

        // Try to determine file's content type
        String contentType = null;
        try {
            contentType = request.getServletContext().getMimeType(resource.getFile().getAbsolutePath());
        } catch (IOException ex) {
//            logger.info("Could not determine file type.");
        }

        // Fallback to the default content type if type could not be determined
        if(contentType == null) {
            contentType = "application/octet-stream";
        }

        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType(contentType))
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + resource.getFilename() + "\"")
                .body(resource);
    }
}
