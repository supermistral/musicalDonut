from rest_framework.permissions import BasePermission


class StaffPermission(BasePermission):
    """
    Принадлежность к группе модераторов
    """

    message = "You don't have permission to do this"

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_staff