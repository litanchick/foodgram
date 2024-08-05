from rest_framework.pagination import LimitOffsetPagination

from .constants import PAGE_SIZE_PAGINATION


class LimitNumber(LimitOffsetPagination):
    page_size = PAGE_SIZE_PAGINATION
    page_size_query_param = 'limit'
