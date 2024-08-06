from rest_framework.pagination import PageNumberPagination

from .constants import PAGE_SIZE_PAGINATION


class PageLimitPagination(PageNumberPagination):
    page_size = PAGE_SIZE_PAGINATION
    page_size_query_param = "limit"
