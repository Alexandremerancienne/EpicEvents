from rest_framework import permissions


class IsManagerOrSalesContact(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        sales_contact = obj.sales_contact
        return (
            True
            if request.user.role
            == "management" or sales_contact == request.user
            else False
        )


class IsManagerOrClientSalesContact(IsManagerOrSalesContact):
    message = (
        "Missing credentials: "
        "Client information can be modified "
        "only by Management or Sales contact"
    )


class IsManagerOrContractSalesContact(IsManagerOrSalesContact):
    message = (
        "Missing credentials: "
        "Contract information can be modified "
        "only by Management or Sales contact"
    )


class IsManagerOrEventSupportContact(permissions.BasePermission):
    message = (
        "Missing credentials: "
        "Event information can be modified "
        "only by Management or Support contact"
    )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        support_contact = obj.support_contact
        return (
            True
            if request.user.role ==
            "management" or support_contact == request.user
            else False
        )


class IsManager(permissions.BasePermission):
    message = "Missing credentials: User can be deleted " \
              "only by Management"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return True if request.user.role == "management" else False


class IsManagerOrNoteEventSupportContact(permissions.BasePermission):
    message = (
        "Missing credentials: "
        "Event information can be modified "
        "only by Management or Support contact"
    )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            True
            if request.user.role == "management"
            or obj.event.support_contact == request.user
            else False
        )
