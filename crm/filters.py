from django_filters import rest_framework as filters

from accounts.models import User
from crm.models import Client, Contract, Event, Note


class UserFilter(filters.FilterSet):
    """Implements filters to be used with UserViewSet."""

    username_contains = filters.CharFilter(field_name="username",
                                           lookup_expr="icontains")

    class Meta:
        model = User
        fields = ["username", "role", "username_contains"]


class ClientFilter(filters.FilterSet):
    """Implements filters to be used with ClientViewSet."""

    first_name__contains = filters.CharFilter(field_name="first_name",
                                              lookup_expr="icontains")
    first_name = filters.CharFilter(field_name="first_name",
                                    lookup_expr="iexact")
    last_name = filters.CharFilter(field_name="last_name",
                                   lookup_expr="iexact")
    last_name__contains = filters.CharFilter(field_name="last_name",
                                             lookup_expr="icontains")
    company = filters.CharFilter(field_name="company",
                                 lookup_expr="iexact")

    class Meta:
        model = Client
        fields = ["first_name", "first_name__contains",
                  "last_name__contains", "last_name",
                  "company", "sales_contact"]


class ContractFilter(filters.FilterSet):
    """Implements filters to be used with ContractViewSet."""

    class Meta:
        model = Contract
        fields = ["status", "client", "sales_contact"]


class EventFilter(filters.FilterSet):
    """Implements filters to be used with EventViewSet."""

    class Meta:
        model = Event
        fields = ["event_over", "client", "support_contact"]


class NoteFilter(filters.FilterSet):
    """Implements filters to be used with NoteViewSet."""

    description__contains = filters.CharFilter(field_name="description",
                                               lookup_expr="icontains")

    class Meta:
        model = Note
        fields = ["description__contains"]
