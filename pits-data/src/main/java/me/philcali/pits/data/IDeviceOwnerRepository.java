package me.philcali.pits.data;

import java.util.Optional;

import me.philcali.db.api.Conditions;
import me.philcali.db.api.QueryParams;
import me.philcali.db.api.QueryResult;
import me.philcali.pits.data.model.IDeviceOwner;

public interface IDeviceOwnerRepository {
    static final String OWNER_ID = "ownerId";
    static final String DEVICE_ID = "deviceId";

    Optional<IDeviceOwner> get(final String deviceId, final String ownerId);

    default QueryResult<IDeviceOwner> listDevicesByOwner(final String ownerId) {
        return listItems(QueryParams.builder()
                .withConditions(Conditions.attribute(OWNER_ID).equalsTo(ownerId))
                .build());
    }

    QueryResult<IDeviceOwner> listItems(QueryParams params);

    default QueryResult<IDeviceOwner> listOwnersByDevice(final String deviceId) {
        return listItems(QueryParams.builder()
                .withConditions(Conditions.attribute(DEVICE_ID).equalsTo(deviceId))
                .build());
    }
}
