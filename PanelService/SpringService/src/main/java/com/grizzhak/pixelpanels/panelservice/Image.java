package com.grizzhak.pixelpanels.panelservice;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;
import javax.persistence.Lob;

@Entity
class Image {

    private @Id
    @GeneratedValue
    Long id;

    private String filename;

    @Lob
    byte[] data;

    Image() {}

    Image(String filename) {
        this.filename = filename;
    }

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getFilename() {
        return this.filename;
    }

    public void setFilename(String filename) {
        this.filename = filename;
    }

    public byte[] getData() {
        return data;
    }

    public void setData(byte[] data) {
        this.data = data;
    }
//
//    @Override
//    public boolean equals(Object o) {
//
//        if (this == o)
//            return true;
//        if (!(o instanceof Image))
//            return false;
//        Image panel = (Image) o;
//        return Objects.equals(this.id, panel.id) && Objects.equals(this.imagePath, panel.imagePath);
//    }
//
//    @Override
//    public int hashCode() {
//        return Objects.hash(this.id, this.imagePath);
//    }
//
//    @Override
//    public String toString() {
//        return "Panel{" + "id=" + this.id + ", name='" + this.imagePath + '\'' + '}';
//    }
}