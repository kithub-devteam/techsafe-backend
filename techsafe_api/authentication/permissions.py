from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.idrole and
            request.user.idrole.role == 'admin'
        )

class IsResearcher(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.idrole and
            request.user.idrole.role == 'chercheur'
        )

class IsYouth(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.idrole and
            request.user.idrole.role == 'jeune'
        )

class IsDirectActor(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.idrole and
            request.user.idrole.role == 'acteur_direct'
        )

class IsIndirectActor(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.idrole and
            request.user.idrole.role == 'acteur_indirect'
        )