package me.philcali.pits.data;

import me.philcali.pits.data.model.IDeviceOwner;
import me.philcali.pits.data.query.Filters;
import me.philcali.pits.data.query.QueryParams;
import me.philcali.pits.data.query.QueryResult;

public interface IDeviceOwnerRepository {
    static final String OWNER_ID = "ownerId";
    static final String DEVICE_ID = "deviceId";

    default QueryResult<IDeviceOwner> listDevicesByOwner(final String ownerId) {
        return listItems(QueryParams.builder()
                .withFilters(Filters.attribute(OWNER_ID).equalsTo(ownerId))
                .build());
    }

    QueryResult<IDeviceOwner> listItems(QueryParams params);

    default QueryResult<IDeviceOwner> listOwnersByDevice(final String deviceId) {
        return listItems(QueryParams.builder()
                .withFilters(Filters.attribute(DEVICE_ID).equalsTo(deviceId))
                .build());
    }
}
