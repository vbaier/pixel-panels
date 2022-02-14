package com.grizzhak.pixelpanels.panelservice;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class GuiController {
    @GetMapping("/upload_image")
    String uploadImage() {

        return "image_upload";
    }
}
