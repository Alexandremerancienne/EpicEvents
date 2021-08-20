from django_filters import rest_framework as filters

from accounts.models import User
from crm.models import Client, Contract, Event, Note


class UserFilter(filters.FilterSet):
    username_contains = filters.CharFilter(
        field_name="username", lookup_expr="icontains"
    )

    class Meta:
        model = User
        fields = ["username", "role", "username_contains"]


class ClientFilter(filters.FilterSet):
    first_name__contains = filters.CharFilter(
        field_name="first_name", lookup_expr="icontains"
    )
    first_name = filters.CharFilter(field_name="first_name",
                                    lookup_expr="iexact")
    last_name = filters.CharFilter(field_name="last_name",
                                   lookup_expr="iexact")
    company = filters.CharFilter(field_name="company", lookup_expr="iexact")

    class Meta:
        model = Client
        fields = [
            "first_name",
            "first_name__contains",
            "last_name",
            "company",
            "sales_contact",
        ]


class ContractFilter(filters.FilterSet):
    class Meta:
        model = Contract
        fields = ["status", "client", "sales_contact"]


class EventFilter(filters.FilterSet):
    class Meta:
        model = Event
        fields = ["event_over", "client", "support_contact"]


class NoteFilter(filters.FilterSet):
    description__contains = filters.CharFilter(
        field_name="description", lookup_expr="icontains"
    )

    class Meta:
        model = Note
        fields = ["description__contains"]
