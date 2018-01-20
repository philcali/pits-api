package me.philcali.pits.data.model.transfer;

import me.philcali.pits.data.model.IDeviceOwner;

public class DeviceOwner implements IDeviceOwner {
    public static class Builder {
        private String deviceId;
        private String owner;
        private Permission permission = Permission.VIEW;


        public DeviceOwner build() {
            return new DeviceOwner(this);
        }

        public String getDeviceId() {
            return deviceId;
        }

        public String getOwner() {
            return owner;
        }

        public Permission getPermission() {
            return permission;
        }

        public Builder setOwner(final String owner) {
            this.owner = owner;
            return this;
        }

        public Builder setPermission(final Permission permission) {
            this.permission = permission;
            return this;
        }

        public Builder withDeviceId(final String deviceId) {
            this.deviceId = deviceId;
            return this;
        }
    }

    private String deviceId;
    private String owner;
    private Permission permission;

    public DeviceOwner() {
    }

    private DeviceOwner(final Builder builder) {
        this.deviceId = builder.getDeviceId();
        this.owner = builder.getOwner();
        this.permission = builder.getPermission();
    }

    @Override
    public boolean equals(final Object obj) {
        if (this == obj)
            return true;
        if (obj == null)
            return false;
        if (getClass() != obj.getClass())
            return false;
        final DeviceOwner other = (DeviceOwner) obj;
        if (deviceId == null) {
            if (other.deviceId != null)
                return false;
        } else if (!deviceId.equals(other.deviceId))
            return false;
        if (owner == null) {
            if (other.owner != null)
                return false;
        } else if (!owner.equals(other.owner))
            return false;
        if (permission != other.permission)
            return false;
        return true;
    }

    @Override
    public String getDeviceId() {
        return deviceId;
    }

    @Override
    public String getOwner() {
        return owner;
    }

    @Override
    public Permission getPermission() {
        return permission;
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((deviceId == null) ? 0 : deviceId.hashCode());
        result = prime * result + ((owner == null) ? 0 : owner.hashCode());
        result = prime * result + ((permission == null) ? 0 : permission.hashCode());
        return result;
    }

    public void setDeviceId(final String deviceId) {
        this.deviceId = deviceId;
    }

    public void setOwner(final String owner) {
        this.owner = owner;
    }

    public void setPermission(final Permission permission) {
        this.permission = permission;
    }
}
