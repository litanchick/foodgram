from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)

from .constants import PAGE_SIZE_PAGINATION


class LimitNumber(LimitOffsetPagination):
    page_size = PAGE_SIZE_PAGINATION
    page_size_query_param = 'limit'


class PaginationNumber(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page'
    max_page_size = 100
