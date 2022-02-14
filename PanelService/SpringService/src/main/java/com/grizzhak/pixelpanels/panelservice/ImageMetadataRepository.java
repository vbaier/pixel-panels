package com.grizzhak.pixelpanels.panelservice;

import org.springframework.data.jpa.repository.JpaRepository;

public interface ImageMetadataRepository extends JpaRepository<Image, Long> {
}
