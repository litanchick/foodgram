from rest_framework.permissions import (
    IsAuthenticated, AllowAny, BasePermission
)
from rest_framework import permissions


class CustomPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous and (
            request.method in ['list', 'retrieve', 'GET']
        ):
            return 'rest_framework.permissions.AllowAny'
        else:
            return 'rest_framework.permissions.IsAuthenticated'


class RecipePermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

    def has_permission(self, request, view):
        if request.user.is_anonymous and (
            request.method not in permissions.SAFE_METHODS
        ):
            return False
        else:
            return True
