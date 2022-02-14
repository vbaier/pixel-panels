package com.grizzhak.pixelpanels.panelservice;


import java.util.Objects;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;

@Entity
class Panel {

    private @Id @GeneratedValue Long id;
    private String imagePath;

    Panel() {}

    Panel(String imagePath) {
        this.imagePath = imagePath;
    }

    public Long getId() {
        return this.id;
    }

    public String getImagePath() {
        return this.imagePath;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public void setImagePath(String name) {
        this.imagePath = imagePath;
    }

    @Override
    public boolean equals(Object o) {

        if (this == o)
            return true;
        if (!(o instanceof Panel))
            return false;
        Panel panel = (Panel) o;
        return Objects.equals(this.id, panel.id) && Objects.equals(this.imagePath, panel.imagePath);
    }

    @Override
    public int hashCode() {
        return Objects.hash(this.id, this.imagePath);
    }

    @Override
    public String toString() {
        return "Panel{" + "id=" + this.id + ", name='" + this.imagePath + '\'' + '}';
    }
}