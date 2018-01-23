package me.philcali.pits.dynamo;

import java.util.function.Function;

import com.amazonaws.SdkBaseException;
import com.amazonaws.services.dynamodbv2.document.Item;
import com.amazonaws.services.dynamodbv2.document.Table;

import me.philcali.db.api.QueryParams;
import me.philcali.db.api.QueryResult;
import me.philcali.db.dynamo.QueryAdapter;
import me.philcali.pits.data.IDeviceOwnerRepository;
import me.philcali.pits.data.exception.DeviceOwnerRepositoryException;
import me.philcali.pits.data.model.IDeviceOwner;
import me.philcali.pits.dynamo.model.DeviceOwnerDynamo;

public class DeviceOwnerRepositoryDynamo implements IDeviceOwnerRepository {
    private final Table owners;

    public DeviceOwnerRepositoryDynamo(final Table owners) {
        this.owners = owners;
    }

    @Override
    public QueryResult<IDeviceOwner> listItems(final QueryParams params) {
        final QueryAdapter adapter = QueryAdapter.builder()
                .withQueryParams(params)
                .withHashKey(OWNER_ID)
                .withIndexMap(DEVICE_ID, owners.getIndex("deviceId-index"))
                .build();
        final Function<Item, IDeviceOwner> thunk = DeviceOwnerDynamo::new;
        try {
            return adapter.andThen(result -> result.map(thunk)).apply(owners);
        } catch (SdkBaseException e) {
            throw new DeviceOwnerRepositoryException(e);
        }
    }
}
