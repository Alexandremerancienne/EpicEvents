from django_filters import rest_framework as filters

from accounts.models import User
from crm.models import Client, Contract, Event


class UserFilter(filters.FilterSet):
    username_contains = filters.CharFilter(field_name="username", lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['username', 'role', 'username_contains']


class ClientFilter(filters.FilterSet):
    first_name__contains = filters.CharFilter(field_name="first_name", lookup_expr='icontains')
    first_name = filters.CharFilter(field_name="first_name", lookup_expr='iexact')
    last_name = filters.CharFilter(field_name="last_name", lookup_expr='iexact')
    company = filters.CharFilter(field_name="company", lookup_expr='iexact')
    sales_contact = filters.NumberFilter(field_name="sales_contact", lookup_expr='exact')

    class Meta:
        model = Client
        fields = ['first_name',
                  'first_name__contains',
                  'last_name',
                  'company',
                  'sales_contact'
                  ]


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
