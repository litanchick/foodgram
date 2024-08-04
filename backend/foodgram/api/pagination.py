from rest_framework.pagination import PageNumberPagination

from .constants import PAGE_SIZE_PAGINATION


class LimitNumber(PageNumberPagination):
    page_size = PAGE_SIZE_PAGINATION
    page_size_query_param = 'limit'
    max_page_size = 100
