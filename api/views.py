from rest_framework import viewsets
from rest_framework.response import Response

from .models import Client, Contract, Event
from .serializers import ClientSerializer, ContractSerializer, EventSerializer
from .exceptions import (
    MissingCredentials,
    ClientNotFound,
    ContractNotFound,
    EventNotFound,
    NotInChargeOfClient,
    NotInChargeOfContract,
    NotInChargeOfEvent
)


class ClientViewSet(viewsets.ModelViewSet):

    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def list(self, request):
        user = self.request.user
        if user.role == 'management':
            queryset = Client.objects.all()
        elif user.role == 'sales':
            queryset = Client.objects.filter(sales_contact=user)
        elif user.role == 'support':
            followed_events = Event.objects.filter(support_contact=user)
            followed_events_clients = [event.client.id for event in followed_events]
            queryset = Client.objects.filter(id__in=followed_events_clients)
        else:
            raise MissingCredentials()
        serializer = ClientSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = request.user
        client = Client.objects.filter(id=pk)
        if user.role == 'management':
            queryset = Client.objects.filter(id=pk)
            if queryset.count() == 0:
                raise ClientNotFound()
        elif user.role == 'sales':
            queryset = Client.objects.filter(id=pk, sales_contact=user)
            if client.count() == 0 and queryset.count() == 0:
                raise ClientNotFound()
            elif client.count() != 0 and queryset.count() == 0:
                raise NotInChargeOfClient()
        elif user.role == 'support':
            followed_events = Event.objects.filter(support_contact=user)
            followed_events_clients = [event.client.id for event in followed_events]
            queryset = Client.objects.filter(id__in=followed_events_clients, id=pk)
            if client.count() == 0 and queryset.count() == 0:
                raise ClientNotFound()
            elif client.count() != 0 and queryset.count() == 0:
                raise NotInChargeOfClient()
        else:
            raise MissingCredentials()

        retrieved_client = queryset.first()
        serializer = ClientSerializer(retrieved_client)
        return Response(serializer.data)


class ContractViewSet(viewsets.ModelViewSet):

    queryset = Contract.objects.all()
    serializer_class = ContractSerializer

    def list(self, request):
        user = self.request.user
        if user.role == 'management':
            queryset = Contract.objects.all()
        elif user.role == 'sales':
            queryset = Contract.objects.filter(sales_contact=user)
        elif user.role == 'support':
            raise MissingCredentials()
        else:
            raise MissingCredentials()
        serializer = ContractSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = request.user
        contract = Contract.objects.filter(id=pk)
        if user.role == 'management':
            queryset = Contract.objects.filter(id=pk)
            if queryset.count() == 0:
                raise ContractNotFound()
        elif user.role == 'sales':
            queryset = Contract.objects.filter(id=pk, sales_contact=user)
            if contract.count() == 0 and queryset.count() == 0:
                raise ContractNotFound()
            elif contract.count() != 0 and queryset.count() == 0:
                raise NotInChargeOfContract()
        elif user.role == 'support':
            raise NotInChargeOfContract()
        else:
            raise MissingCredentials()

        retrieved_contract = queryset.first()
        serializer = ContractSerializer(retrieved_contract)
        return Response(serializer.data)


class EventViewSet(viewsets.ModelViewSet):

    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def list(self, request):
        user = self.request.user
        if user.role == 'management':
            queryset = Event.objects.all()
        elif user.role == 'sales':
            queryset = Event.objects.filter(client__sales_contact=user)
        elif user.role == 'support':
            queryset = Event.objects.filter(support_contact=user)
        else:
            raise MissingCredentials()
        serializer = EventSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = request.user
        event = Event.objects.filter(id=pk)
        if user.role == 'management':
            queryset = Event.objects.filter(id=pk)
            if queryset.count() == 0:
                raise EventNotFound()
        elif user.role == 'sales':
            queryset = Event.objects.filter(id=pk, client__sales_contact=user)
            if event.count() == 0 and queryset.count() == 0:
                raise EventNotFound()
            elif event.count() != 0 and queryset.count() == 0:
                raise NotInChargeOfEvent()
        elif user.role == 'support':
            queryset = Event.objects.filter(id=pk, support_contact=user)
            if event.count() == 0 and queryset.count() == 0:
                raise EventNotFound()
            elif event.count() != 0 and queryset.count() == 0:
                raise NotInChargeOfEvent()
        else:
            raise MissingCredentials()

        retrieved_event = queryset.first()
        serializer = EventSerializer(retrieved_event)
        return Response(serializer.data)
