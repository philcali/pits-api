package me.philcali.pits.data.model;

public interface ISystemInformation {
    double getCpuUtilization();
    long getTotalMemoryBytes();
    long getUsedMemoryBytes();
}
