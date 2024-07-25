from rest_framework import pagination


class PaginationNumber(pagination.PageNumberPagination):
    page_size = 3
    page_size_query_param = 'limit'
    max_page_size = 100
