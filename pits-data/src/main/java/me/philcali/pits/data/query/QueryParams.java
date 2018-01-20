package me.philcali.pits.data.query;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class QueryParams {
    public static class Builder {
        private int maxSize = DEFAULT_MAX_SIZE;
        private IPageKey token;
        private List<IFilter> filters = new ArrayList<>();

        public QueryParams build() {
            return new QueryParams(this);
        }

        public List<IFilter> getFilters() {
            return filters;
        }

        public int getMaxSize() {
            return maxSize;
        }

        public IPageKey getToken() {
            return token;
        }

        public Builder withFilters(final IFilter ... filters) {
            Arrays.stream(filters).forEach(this.filters::add);
            return this;
        }

        public Builder withFilters(final List<IFilter> filters) {
            this.filters = filters;
            return this;
        }

        public Builder withMaxSize(final int maxSize) {
            this.maxSize = maxSize;
            return this;
        }

        public Builder withToken(final IPageKey token) {
            this.token = token;
            return this;
        }
    }

    public static final int DEFAULT_MAX_SIZE = 100;

    public static Builder builder() {
        return new Builder();
    }

    private final IPageKey token;
    private final int maxSize;
    private final List<IFilter> filters;

    public QueryParams(final Builder builder) {
        this.filters = builder.getFilters();
        this.maxSize = builder.getMaxSize();
        this.token = builder.getToken();
    }

    public List<IFilter> getFilters() {
        return filters;
    }

    public int getMaxSize() {
        return maxSize;
    }

    public IPageKey getToken() {
        return token;
    }
}
