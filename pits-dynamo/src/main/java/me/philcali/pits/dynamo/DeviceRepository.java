package me.philcali.pits.dynamo;

import java.util.List;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;

import com.amazonaws.SdkBaseException;
import com.amazonaws.services.dynamodbv2.document.DynamoDB;
import com.amazonaws.services.dynamodbv2.document.Item;
import com.amazonaws.services.dynamodbv2.document.PrimaryKey;
import com.amazonaws.services.dynamodbv2.document.Table;

import me.philcali.pits.data.IDeviceRepository;
import me.philcali.pits.data.exception.DeviceRepositoryException;
import me.philcali.pits.data.model.IDevice;
import me.philcali.pits.data.model.IDeviceOwner;
import me.philcali.pits.dynamo.model.DeviceDynamo;
import me.philcali.pits.dynamo.query.BatchGetAdapter;

public class DeviceRepository implements IDeviceRepository {
    private final DynamoDB db;
    private final Table devices;

    public DeviceRepository(final DynamoDB db, final Table devices) {
        this.db = db;
        this.devices = devices;
    }

    @Override
    public List<IDevice> batchGetByOwners(final List<IDeviceOwner> owners) {
        final Function<List<PrimaryKey>, List<Item>> batcher = new BatchGetAdapter(db, devices.getTableName());
        return batcher.compose(this::transformOwnersToKeys).andThen(this::transformItemsToDevices).apply(owners);
    }

    @Override
    public Optional<IDevice> get(final String deviceId) {
        try {
            return Optional.ofNullable(devices.getItem(DeviceDynamo.ID, deviceId))
                    .map(DeviceDynamo::new);
        } catch (SdkBaseException e) {
            throw new DeviceRepositoryException(e);
        }
    }

    @Override
    public void save(final IDevice device) {
        try {
            devices.putItem(DeviceDynamo.toItem(device));
        } catch (SdkBaseException e) {
            throw new DeviceRepositoryException(e);
        }
    }

    private List<IDevice> transformItemsToDevices(final List<Item> items) {
        return items.stream().map(DeviceDynamo::new).collect(Collectors.toList());
    }

    private List<PrimaryKey> transformOwnersToKeys(final List<IDeviceOwner> owners) {
        return owners.stream()
                .map(owner -> new PrimaryKey().addComponent(DeviceDynamo.ID, owner.getDeviceId()))
                .collect(Collectors.toList());
    }

}
