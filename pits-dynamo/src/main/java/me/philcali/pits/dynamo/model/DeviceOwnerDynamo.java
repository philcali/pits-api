package me.philcali.pits.dynamo.model;

import java.util.Optional;

import com.amazonaws.services.dynamodbv2.document.Item;

import me.philcali.pits.data.model.IDeviceOwner;

public class DeviceOwnerDynamo implements IDeviceOwner {
    public static final String OWNER_ID = "ownerId";
    public static final String DEVICE_ID = "deviceId";
    public static final String PERMISSION = "permission";

    public static Item toItem(final IDeviceOwner deviceOwner) {
        return new Item()
                .withString(OWNER_ID, deviceOwner.getDeviceId())
                .withString(DEVICE_ID, deviceOwner.getDeviceId())
                .withString(PERMISSION, deviceOwner.getPermission().name());
    }

    private final Item item;

    public DeviceOwnerDynamo(final Item item) {
        this.item = item;
    }

    @Override
    public String getDeviceId() {
        return item.getString(DEVICE_ID);
    }

    @Override
    public String getOwner() {
        return item.getString(OWNER_ID);
    }

    @Override
    public Permission getPermission() {
        return Optional.ofNullable(item.getString(PERMISSION))
                .map(Permission::valueOf)
                .orElse(Permission.VIEW);
    }

}
