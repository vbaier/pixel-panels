package com.grizzhak.pixelpanels.panelservice;

public class PanelNotFoundException extends RuntimeException {

    PanelNotFoundException(Long id) {
        super("Could not find panel " + id);
    }
}