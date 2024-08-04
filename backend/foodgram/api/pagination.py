from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)


class LimitNumber(LimitOffsetPagination):
    page_size = 6
    page_size_query_param = 'limit'
    max_page_size = 100


class PaginationNumber(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page'
    max_page_size = 100
