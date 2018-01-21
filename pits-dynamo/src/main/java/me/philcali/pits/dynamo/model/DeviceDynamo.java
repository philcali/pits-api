package me.philcali.pits.dynamo.model;

import java.util.Date;

import com.amazonaws.services.dynamodbv2.document.Item;

import me.philcali.pits.data.model.IDevice;
import me.philcali.pits.data.model.ISystemInformation;

public class DeviceDynamo implements IDevice {
    public static final String ID = "id";
    public static final String MAC_ADDRESS = "macAddress";
    public static final String SYS_INFO = "systemInformation";
    public static final String VERSION = "version";
    public static final String LAST_UPDATE = "lastUpdate";

    public static Item toItem(final IDevice device) {
        return new Item()
                .withString(ID, device.getId())
                .withString(MAC_ADDRESS, device.getMacAddress())
                .withString(VERSION, device.getVersion())
                .withMap(SYS_INFO, SystemInformationDynamo.toItem(device.getSystemInformation()).asMap())
                .withLong(LAST_UPDATE, device.getLastUpdate().getTime());
    }

    private final Item item;

    public DeviceDynamo(final Item item) {
        this.item = item;
    }

    @Override
    public String getId() {
        return item.getString(ID);
    }

    @Override
    public Date getLastUpdate() {
        return new Date(item.getLong(LAST_UPDATE));
    }

    @Override
    public String getMacAddress() {
        return item.getString(MAC_ADDRESS);
    }

    @Override
    public ISystemInformation getSystemInformation() {
        return new SystemInformationDynamo(Item.fromMap(item.getMap(SYS_INFO)));
    }

    @Override
    public String getVersion() {
        return item.getString(VERSION);
    }

}
