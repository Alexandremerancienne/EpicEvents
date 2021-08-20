from django_filters import rest_framework as filters

from accounts.models import User
from crm.models import Client, Contract, Event


class UserFilter(filters.FilterSet):
    username_contains = filters.CharFilter(field_name="username", lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['username', 'role', 'username_contains']


class ClientFilter(filters.FilterSet):

    class Meta:
        model = Client
        fields = {
            'first_name': ['icontains'],
            'last_name': ['iexact'],
            'email': ['iexact'],
            'company': ['iexact'],
            'sales_contact': ['exact'],
        }


class ContractFilter(filters.FilterSet):

    class Meta:
        model = Contract
        fields = {
            'status': ['exact'],
            'client': ['exact'],
            'sales_contact': ['exact'],
        }


class EventFilter(filters.FilterSet):

    class Meta:
        model = Event
        fields = {
            'event_over': ['exact'],
            'client': ['exact'],
            'support_contact': ['exact'],
        }
