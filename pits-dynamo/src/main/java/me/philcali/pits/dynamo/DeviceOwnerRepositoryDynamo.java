package me.philcali.pits.dynamo;

import java.util.Optional;
import java.util.function.Function;

import com.amazonaws.SdkBaseException;
import com.amazonaws.services.dynamodbv2.document.Item;
import com.amazonaws.services.dynamodbv2.document.Table;

import me.philcali.db.api.QueryParams;
import me.philcali.db.api.QueryResult;
import me.philcali.db.dynamo.IRetrievalStrategy;
import me.philcali.db.dynamo.QueryRetrievalStrategy;
import me.philcali.pits.data.IDeviceOwnerRepository;
import me.philcali.pits.data.exception.DeviceOwnerRepositoryException;
import me.philcali.pits.data.model.IDeviceOwner;
import me.philcali.pits.dynamo.model.DeviceOwnerDynamo;


public class DeviceOwnerRepositoryDynamo implements IDeviceOwnerRepository {
    private final Table owners;
    private final IRetrievalStrategy query;

    public DeviceOwnerRepositoryDynamo(final Table owners) {
        this(owners, QueryRetrievalStrategy.fromTable(owners));
    }

    public DeviceOwnerRepositoryDynamo(final Table owners, final IRetrievalStrategy query) {
        this.owners = owners;
        this.query = query;
    }

    @Override
    public Optional<IDeviceOwner> get(final String deviceId, final String ownerId) {
        return Optional.ofNullable(owners.getItem(DEVICE_ID, deviceId, OWNER_ID, ownerId))
                .map(DeviceOwnerDynamo::new);
    }

    @Override
    public QueryResult<IDeviceOwner> listItems(final QueryParams params) {
        try {
            final Function<Item, IDeviceOwner> thunk = DeviceOwnerDynamo::new;
            return query.andThen(result -> result.map(thunk)).apply(params, owners);
        } catch (SdkBaseException e) {
            throw new DeviceOwnerRepositoryException(e);
        }
    }
}
