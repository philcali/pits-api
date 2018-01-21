package me.philcali.pits.dynamo.model;

import com.amazonaws.services.dynamodbv2.document.Item;

import me.philcali.pits.data.model.IUser;

public class UserDynamo implements IUser {
    public static final String EMAIL_ADDRESS = "emailAddress";
    public static final String IMAGE = "image";
    public static final String FIRST_NAME = "firstName";
    public static final String LAST_NAME = "lastName";

    public static Item toItem(final IUser user) {
        return new Item()
                .withString(EMAIL_ADDRESS, user.getEmailAddress())
                .withString(IMAGE, user.getImage())
                .withString(FIRST_NAME, user.getFirstName())
                .withString(LAST_NAME, user.getLastName());
    }

    private final Item item;

    public UserDynamo(final Item item) {
        this.item = item;
    }

    @Override
    public String getEmailAddress() {
        return item.getString(EMAIL_ADDRESS);
    }

    @Override
    public String getFirstName() {
        return item.getString(FIRST_NAME);
    }

    @Override
    public String getImage() {
        return item.getString(IMAGE);
    }

    @Override
    public String getLastName() {
        return item.getString(LAST_NAME);
    }

}
