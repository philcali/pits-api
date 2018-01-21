package me.philcali.pits.dynamo.model;

import com.amazonaws.services.dynamodbv2.document.Item;

import me.philcali.pits.data.model.ISystemInformation;

public class SystemInformationDynamo implements ISystemInformation {
    public static final String CPU_UTIL = "cpuUtilization";
    public static final String TOTAL_MEMORY = "totalMemoryBytes";
    public static final String USED_MEMORY = "usedMemoryBytes";

    public static Item toItem(final ISystemInformation systemInformation) {
        return new Item()
                .withDouble(CPU_UTIL, systemInformation.getCpuUtilization())
                .withLong(TOTAL_MEMORY, systemInformation.getTotalMemoryBytes())
                .withLong(USED_MEMORY, systemInformation.getUsedMemoryBytes());
    }

    private final Item item;

    public SystemInformationDynamo(final Item item) {
        this.item = item;
    }

    @Override
    public double getCpuUtilization() {
        return item.getDouble(CPU_UTIL);
    }

    @Override
    public long getTotalMemoryBytes() {
        return item.getLong(TOTAL_MEMORY);
    }

    @Override
    public long getUsedMemoryBytes() {
        return item.getLong(USED_MEMORY);
    }

}
