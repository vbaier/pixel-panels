package com.grizzhak.pixelpanels.panelservice;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.stereotype.Repository;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

@Repository
class ImageFileRepository {

    @Value("${image.storage-dir}")
    String ImagesRootPath;

    String saveImageFile(byte[] data, String imageName) throws Exception {
        Path newFile = Paths.get(ImagesRootPath + imageName);
        Files.createDirectories(newFile.getParent());

        Files.write(newFile, data);

        return newFile.toAbsolutePath()
                .toString();
    }

    FileSystemResource getImageFile(String imageName) {
        try {
            return new FileSystemResource(Paths.get(ImagesRootPath + imageName));
        } catch (Exception e) {
            // Handle access or file not found problems.
            throw new RuntimeException();
        }
    }
}