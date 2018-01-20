package me.philcali.pits.data.model.transfer;

import java.util.Date;

import me.philcali.pits.data.model.IDevice;
import me.philcali.pits.data.model.ISystemInformation;

public class Device implements IDevice {
    public static class Builder {
        private String id;
        private String macAddress;
        private SystemInformation systemInformation;
        private Date lastUpdate;
        private String version;

        public Device build() {
            return new Device(this);
        }

        public String getId() {
            return id;
        }

        public Date getLastUpdate() {
            return lastUpdate;
        }

        public String getMacAddress() {
            return macAddress;
        }

        public SystemInformation getSystemInformation() {
            return systemInformation;
        }

        public String getVersion() {
            return version;
        }

        public Builder withId(final String id) {
            this.id = id;
            return this;
        }

        public Builder withLastUpdate(final Date lastUpdate) {
            this.lastUpdate = lastUpdate;
            return this;
        }

        public Builder withMacAddress(final String macAddress) {
            this.macAddress = macAddress;
            return this;
        }

        public Builder withSystemInformation(final SystemInformation systemInformation) {
            this.systemInformation = systemInformation;
            return this;
        }

        public Builder withVersion(final String version) {
            this.version = version;
            return this;
        }
    }

    private String id;
    private String macAddress;
    private SystemInformation systemInformation;
    private Date lastUpdate;
    private String version;

    public Device() {
    }

    private Device(final Builder builder) {
        this.id = builder.getId();
        this.macAddress = builder.getMacAddress();
        this.lastUpdate = builder.getLastUpdate();
        this.version = builder.getVersion();
        this.systemInformation = builder.getSystemInformation();
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj)
            return true;
        if (obj == null)
            return false;
        if (getClass() != obj.getClass())
            return false;
        Device other = (Device) obj;
        if (id == null) {
            if (other.id != null)
                return false;
        } else if (!id.equals(other.id))
            return false;
        if (lastUpdate == null) {
            if (other.lastUpdate != null)
                return false;
        } else if (!lastUpdate.equals(other.lastUpdate))
            return false;
        if (macAddress == null) {
            if (other.macAddress != null)
                return false;
        } else if (!macAddress.equals(other.macAddress))
            return false;
        if (systemInformation == null) {
            if (other.systemInformation != null)
                return false;
        } else if (!systemInformation.equals(other.systemInformation))
            return false;
        if (version == null) {
            if (other.version != null)
                return false;
        } else if (!version.equals(other.version))
            return false;
        return true;
    }

    @Override
    public String getId() {
        return id;
    }

    @Override
    public Date getLastUpdate() {
        return lastUpdate;
    }

    @Override
    public String getMacAddress() {
        return macAddress;
    }

    @Override
    public ISystemInformation getSystemInformation() {
        return systemInformation;
    }

    @Override
    public String getVersion() {
        return version;
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((id == null) ? 0 : id.hashCode());
        result = prime * result + ((lastUpdate == null) ? 0 : lastUpdate.hashCode());
        result = prime * result + ((macAddress == null) ? 0 : macAddress.hashCode());
        result = prime * result + ((systemInformation == null) ? 0 : systemInformation.hashCode());
        result = prime * result + ((version == null) ? 0 : version.hashCode());
        return result;
    }

    public void setId(String id) {
        this.id = id;
    }

    public void setLastUpdate(Date lastUpdate) {
        this.lastUpdate = lastUpdate;
    }

    public void setMacAddress(String macAddress) {
        this.macAddress = macAddress;
    }

    public void setSystemInformation(SystemInformation systemInformation) {
        this.systemInformation = systemInformation;
    }

    public void setVersion(String version) {
        this.version = version;
    }

}
