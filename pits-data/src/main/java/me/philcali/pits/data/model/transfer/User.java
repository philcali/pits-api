package me.philcali.pits.data.model.transfer;

import me.philcali.pits.data.model.IUser;

public class User implements IUser {
    public static class Builder {
        private String emailAddress;
        private String firstName;
        private String lastName;
        private String image;

        public User build() {
            return new User(this);
        }

        public String getEmailAddress() {
            return emailAddress;
        }

        public String getFirstName() {
            return firstName;
        }

        public String getImage() {
            return image;
        }

        public String getLastName() {
            return lastName;
        }

        public Builder withEmailAddress(final String emailAddress) {
            this.emailAddress = emailAddress;
            return this;
        }

        public Builder withFirstName(final String firstName) {
            this.firstName = firstName;
            return this;
        }

        public Builder withImage(final String image) {
            this.image = image;
            return this;
        }

        public Builder withLastName(final String lastName) {
            this.lastName = lastName;
            return this;
        }
    }

    public static Builder builder() {
        return new Builder();
    }

    private String emailAddress;
    private String firstName;
    private String lastName;
    private String image;

    public User() {
    }

    private User(final Builder builder) {
        this.emailAddress = builder.getEmailAddress();
        this.firstName = builder.getFirstName();
        this.lastName = builder.getLastName();
        this.image = builder.getImage();
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj)
            return true;
        if (obj == null)
            return false;
        if (getClass() != obj.getClass())
            return false;
        User other = (User) obj;
        if (emailAddress == null) {
            if (other.emailAddress != null)
                return false;
        } else if (!emailAddress.equals(other.emailAddress))
            return false;
        if (firstName == null) {
            if (other.firstName != null)
                return false;
        } else if (!firstName.equals(other.firstName))
            return false;
        if (image == null) {
            if (other.image != null)
                return false;
        } else if (!image.equals(other.image))
            return false;
        if (lastName == null) {
            if (other.lastName != null)
                return false;
        } else if (!lastName.equals(other.lastName))
            return false;
        return true;
    }

    @Override
    public String getEmailAddress() {
        return emailAddress;
    }

    @Override
    public String getFirstName() {
        return firstName;
    }

    @Override
    public String getImage() {
        return image;
    }

    @Override
    public String getLastName() {
        return lastName;
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((emailAddress == null) ? 0 : emailAddress.hashCode());
        result = prime * result + ((firstName == null) ? 0 : firstName.hashCode());
        result = prime * result + ((image == null) ? 0 : image.hashCode());
        result = prime * result + ((lastName == null) ? 0 : lastName.hashCode());
        return result;
    }

    public void setEmailAddress(final String emailAddress) {
        this.emailAddress = emailAddress;
    }

    public void setFirstName(final String firstName) {
        this.firstName = firstName;
    }

    public void setImage(final String image) {
        this.image = image;
    }

    public void setLastName(final String lastName) {
        this.lastName = lastName;
    }
}
