from rest_framework import permissions


class IsManager(permissions.BasePermission):
    message = "Missing credentials: Users can be read or edited " \
              "only by Management members"

    def has_permission(self, request, view):
        return True if request.user.role == "management" else False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return True if request.user.role == "management" else False


class IsManagerOrSalesContact(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        sales_contact = obj.sales_contact
        return (
            True if request.user.role == "management"
            or sales_contact == request.user
            else False
        )


class IsManagerOrClientSalesContact(IsManagerOrSalesContact):
    message = ("Client detail can be edited only by Management members "
               "or Sales contact")


class IsManagerOrContractSalesContact(permissions.BasePermission):
    message = ("Contract detail can be read or edited "
               "only by Management members or Sales contact")

    def has_permission(self, request, view):
        return False if request.user.role == "support" else True


class IsManagerOrSupportContact(permissions.BasePermission):
    message = ("Event can be edited only by Management members "
               "or Support contact")

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        support_contact = obj.support_contact
        return (
            True if request.user.role == "management"
            or support_contact == request.user
            else False
        )


class IsManagerOrEventSupportContact(permissions.BasePermission):
    message = ("Note can be edited only by Management members "
               "or Support contact")

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            True if request.user.role == "management"
            or obj.event.support_contact == request.user
            else False
        )
