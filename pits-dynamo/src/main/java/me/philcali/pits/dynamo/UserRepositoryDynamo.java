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

import me.philcali.pits.data.IUserRepository;
import me.philcali.pits.data.exception.UserRepositoryException;
import me.philcali.pits.data.model.IDeviceOwner;
import me.philcali.pits.data.model.IUser;
import me.philcali.pits.dynamo.model.UserDynamo;
import me.philcali.pits.dynamo.query.BatchGetAdapter;

public class UserRepositoryDynamo implements IUserRepository {
    private final DynamoDB db;
    private final Table users;

    public UserRepositoryDynamo(final DynamoDB db, final Table users) {
        this.db = db;
        this.users = users;
    }

    @Override
    public List<IUser> batchGetByOwners(final List<IDeviceOwner> owners) {
        final Function<List<PrimaryKey>, List<Item>> batcher = new BatchGetAdapter(db, users.getTableName());
        return batcher.compose(this::transformOwnersToKeys).andThen(this::transformItemsToUsers).apply(owners);
    }

    @Override
    public Optional<IUser> get(final String emailAddress) {
        try {
            return Optional.ofNullable(users.getItem(UserDynamo.EMAIL_ADDRESS, emailAddress))
                    .map(UserDynamo::new);
        } catch (SdkBaseException e) {
            throw new UserRepositoryException(e);
        }
    }

    @Override
    public void save(final IUser user) {
        try {
            users.putItem(UserDynamo.toItem(user));
        } catch (SdkBaseException e) {
            throw new UserRepositoryException(e);
        }
    }

    private List<IUser> transformItemsToUsers(final List<Item> items) {
        return items.stream().map(UserDynamo::new).collect(Collectors.toList());
    }

    private List<PrimaryKey> transformOwnersToKeys(final List<IDeviceOwner> owners) {
        return owners.stream()
                .map(owner -> new PrimaryKey().addComponent(UserDynamo.EMAIL_ADDRESS, owner.getOwner()))
                .collect(Collectors.toList());
    }
}
