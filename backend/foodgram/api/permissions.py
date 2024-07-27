from rest_framework.permissions import (
    IsAuthenticated, AllowAny, BasePermission
)


class CustomPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous and (
            request.method in ['list', 'retrieve', 'GET']
        ):
            return 'rest_framework.permissions.AllowAny'
        else:
            return 'rest_framework.permissions.IsAuthenticated'


# class CustomPermissions(BasePermission):
#     def has_permission(self, request, view):
#         if request.user.is_anonymous and (
#             request.method in ['list', 'retrieve', 'GET']
#         ):
#             print(request.user)
#             return AllowAny
#         else:
#             return IsAuthenticated
