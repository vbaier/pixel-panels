package com.grizzhak.pixelpanels.panelservice;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
public class ImageStorageService {

    @Autowired
    ImageFileRepository imageFileRepository;
    @Autowired
    ImageMetadataRepository imageMetadataRepository;

    Long save(byte[] bytes, String filename) throws Exception {
        String location = imageFileRepository.saveImageFile(bytes, filename);

        return imageMetadataRepository.save(new Image(filename))
                .getId();
    }

    FileSystemResource find(Long imageId) {
        Image image = imageMetadataRepository.findById(imageId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));

        return imageFileRepository.getImageFile(image.getFilename());
    }
}
