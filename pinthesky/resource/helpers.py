from pinthesky.conversion import sort_filters_for
from ophis.database import MAX_ITEMS, QueryParams


def get_limit(request, default_max=MAX_ITEMS):
    limit = int(request.queryparams.get('limit', default_max))
    return min(MAX_ITEMS, max(1, limit))


def create_query_params(
        request,
        sort_order='ascending',
        sort_field='createTime',
        format=None) -> QueryParams:
    sort_asc = request.queryparams.get('order', sort_order) == 'ascending'
    start_time = request.queryparams.get('startTime', None)
    end_time = request.queryparams.get('endTime', None)
    return QueryParams(
        limit=get_limit(request=request),
        next_token=request.queryparams.get('nextToken', None),
        sort_ascending=sort_asc,
        sort_filters=sort_filters_for(
            field=sort_field,
            start_time=start_time,
            end_time=end_time,
            format=format
        )
    )
