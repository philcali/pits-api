package me.philcali.pits.data.model;

public interface IDeviceOwner {
    static enum Permission {
        ADMIN,  // Remote update + MANAGE
        MANAGE, // Update configuration + VIEW
        VIEW;   // View camera stream only
    }

    String getDeviceId();
    String getOwner();
    Permission getPermission();
}
