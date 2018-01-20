package me.philcali.pits.data.model.transfer;

import me.philcali.pits.data.model.ISystemInformation;

public class SystemInformation implements ISystemInformation {
    private static class Builder {
        private double cpuUtilization;
        private long totalMemoryBytes;
        private long usedMemoryBytes;

        public SystemInformation build() {
            return new SystemInformation(this);
        }

        public double getCpuUtilization() {
            return cpuUtilization;
        }

        public long getTotalMemoryBytes() {
            return totalMemoryBytes;
        }

        public long getUsedMemoryBytes() {
            return usedMemoryBytes;
        }

        public Builder withCpuUtilization(final double cpuUtilization) {
            this.cpuUtilization = cpuUtilization;
            return this;
        }

        public Builder withTotalMemoryBytes(final long totalMemoryBytes) {
            this.totalMemoryBytes = totalMemoryBytes;
            return this;
        }

        public Builder withUsedMemoryBytes(final long usedMemoryBytes) {
            this.usedMemoryBytes = usedMemoryBytes;
            return this;
        }

    }

    private double cpuUtilization;
    private long totalMemoryBytes;
    private long usedMemoryBytes;

    public SystemInformation() {
    }

    private SystemInformation(final Builder builder) {
        this.cpuUtilization = builder.getCpuUtilization();
        this.totalMemoryBytes = builder.getTotalMemoryBytes();
        this.usedMemoryBytes = builder.getUsedMemoryBytes();
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj)
            return true;
        if (obj == null)
            return false;
        if (getClass() != obj.getClass())
            return false;
        SystemInformation other = (SystemInformation) obj;
        if (Double.doubleToLongBits(cpuUtilization) != Double.doubleToLongBits(other.cpuUtilization))
            return false;
        if (totalMemoryBytes != other.totalMemoryBytes)
            return false;
        if (usedMemoryBytes != other.usedMemoryBytes)
            return false;
        return true;
    }

    @Override
    public double getCpuUtilization() {
        return cpuUtilization;
    }

    @Override
    public long getTotalMemoryBytes() {
        return totalMemoryBytes;
    }

    @Override
    public long getUsedMemoryBytes() {
        return usedMemoryBytes;
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        long temp;
        temp = Double.doubleToLongBits(cpuUtilization);
        result = prime * result + (int) (temp ^ (temp >>> 32));
        result = prime * result + (int) (totalMemoryBytes ^ (totalMemoryBytes >>> 32));
        result = prime * result + (int) (usedMemoryBytes ^ (usedMemoryBytes >>> 32));
        return result;
    }

    public void setCpuUtilization(final double cpuUtilization) {
        this.cpuUtilization = cpuUtilization;
    }

    public void setTotalMemoryBytes(final long totalMemoryBytes) {
        this.totalMemoryBytes = totalMemoryBytes;
    }

    public void setUsedMemoryBytes(final long usedMemoryBytes) {
        this.usedMemoryBytes = usedMemoryBytes;
    }
}
