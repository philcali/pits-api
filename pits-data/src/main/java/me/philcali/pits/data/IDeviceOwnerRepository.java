package me.philcali.pits.data;

import java.util.List;

import me.philcali.pits.data.model.IDeviceOwner;
import me.philcali.pits.data.query.Filters;
import me.philcali.pits.data.query.QueryParams;

public interface IDeviceOwnerRepository {
    static final String OWNER_ID = "ownerId";
    static final String DEVICE_ID = "deviceId";

    default List<IDeviceOwner> listDevicesByOwner(final String ownerId) {
        return listItems(QueryParams.builder()
                .withFilters(Filters.attribute(OWNER_ID).equalsTo(ownerId))
                .build());
    }

    List<IDeviceOwner> listItems(QueryParams params);

    default List<IDeviceOwner> listOwnersByDevice(final String deviceId) {
        return listItems(QueryParams.builder()
                .withFilters(Filters.attribute(DEVICE_ID).equalsTo(deviceId))
                .build());
    }
}
