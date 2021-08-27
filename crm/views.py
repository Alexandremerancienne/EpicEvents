from datetime import datetime

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User

from .exceptions import (
    CannotCreateClient,
    CannotCreateNote,
    CannotUpdateProfile,
    ContractAlreadySigned,
    ContractMustBeSigned,
    EventOver,
    NotInChargeOfClient,
    NotInChargeOfContract,
    NotInChargeOfEvent,
    NotSalesMember,
    NotSupportMember,
    ObsoleteDate
)

from .filters import (
    ClientFilter,
    ContractFilter,
    EventFilter,
    NoteFilter,
    UserFilter
)

from .models import Client, Contract, Event, Note

from .permissions import (
    IsManager,
    IsManagerOrClientSalesContact,
    IsManagerOrContractSalesContact,
    IsManagerOrEventSupportContact,
    IsManagerOrSupportContact
)

from .serializers import (
    ClientSerializer,
    ContractSerializer,
    EventSerializer,
    NoteSerializer,
    UserSerializer
)

current_date = datetime.now()
aware_date = timezone.make_aware(current_date)


def check_date(string):
    payment_due = string.split("T")
    payment_due = " ".join(payment_due)
    payment_due = datetime.strptime(payment_due, "%Y-%m-%d %H:%M")
    payment_due = timezone.make_aware(payment_due)
    if payment_due < aware_date:
        raise ObsoleteDate()


class ClientViewSet(viewsets.ModelViewSet):
    """
    A ViewSet to list, retrieve, create and update clients.
    """

    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = (
        IsAuthenticated,
        IsManagerOrClientSalesContact,
    )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ClientFilter

    def list(self, request):
        user = self.request.user
        queryset = Client.objects.all()
        if user.role == "sales":
            queryset = queryset.filter(sales_contact=user)
        elif user.role == "support":
            events = Event.objects.filter(support_contact=user)
            events_clients = [event.client.id for event in events]
            queryset = Client.objects.filter(id__in=events_clients)

        queryset = self.filter_queryset(queryset).order_by("last_name")
        serializer = ClientSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = request.user
        client = get_object_or_404(Client, id=pk)
        queryset = Client.objects.filter(id=pk)
        if user.role == "sales":
            queryset = queryset.filter(sales_contact=user)
        elif user.role == "support":
            events = Event.objects.filter(support_contact=user)
            events_clients = [event.client.id for event in events]
            queryset = Client.objects.filter(id__in=events_clients, id=pk)
        if client is not None and queryset.count() == 0:
            raise NotInChargeOfClient()

        serializer = ClientSerializer(client)
        return Response(serializer.data)

    def create(self, request):
        user = request.user
        request_copy = request.data.copy()
        if user.role == "management":
            sales_contact = request_copy["sales_contact"]
            sales_contact = User.objects.filter(id=sales_contact,
                                                role="sales")
            if sales_contact.count() == 0:
                raise NotSalesMember()
        elif user.role == "sales":
            request_copy["sales_contact"] = user.id
        else:
            raise CannotCreateClient()

        serializer = ClientSerializer(data=request_copy)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        client = get_object_or_404(Client, id=pk)
        if "sales_contact" in request.data.keys():
            sales_contact = request.data["sales_contact"]
            sales_contact = User.objects.filter(id=sales_contact, role="sales")
            if sales_contact.count() == 0:
                raise NotSalesMember()

        self.check_object_permissions(request, client)
        serializer = ClientSerializer(client, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ContractViewSet(viewsets.ModelViewSet):
    """
    A ViewSet to list, retrieve, create and update contracts.
    """

    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = (
        IsAuthenticated,
        IsManagerOrContractSalesContact,
    )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ContractFilter

    def list(self, request):
        user = self.request.user
        queryset = Contract.objects.all()
        if user.role == "sales":
            queryset = queryset.filter(sales_contact=user)

        queryset = self.filter_queryset(queryset).order_by("id")
        serializer = ContractSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = request.user
        contract = get_object_or_404(Contract, id=pk)
        if user.role == "sales":
            queryset = Contract.objects.filter(id=pk, sales_contact=user)
            if contract is not None and queryset.count() == 0:
                raise NotInChargeOfContract()

        serializer = ContractSerializer(contract)
        return Response(serializer.data)

    def create(self, request, pk=None):
        user = request.user
        request_copy = request.data.copy()
        client_form = request_copy["client"]
        client = Client.objects.filter(id=client_form)
        client = client.first()
        if user.role == "management":
            request_copy["sales_contact"] = client.sales_contact.id
        elif user.role == "sales":
            request_copy["sales_contact"] = user.id
            user_clients = Client.objects.filter(sales_contact=request.user.id)
            clients_id = [client.id for client in user_clients]
            if int(request_copy["client"]) not in clients_id:
                raise NotInChargeOfClient()
        if "status" in request_copy.keys():
            new_event = Event(client=client, attendees=0)
            new_event.save()

        if "payment_due" in request_copy.keys():
            check_date(request_copy["payment_due"])

        serializer = ContractSerializer(data=request_copy)
        serializer.is_valid(raise_exception=True)
        serializer.save(sales_contact=user)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        user = request.user
        contract = get_object_or_404(Contract, id=pk)
        if contract.status:
            raise ContractAlreadySigned()
        request_copy = request.data.copy()
        if "status" in request_copy.keys():
            new_event = Event(client=contract.client, attendees=0)
            new_event.save()
        if user.role == "management":
            client = request_copy["client"]
            client = get_object_or_404(Client, id=client)
        else:
            request_copy["client"] = contract.client.id
            client = get_object_or_404(Client, id=request_copy["client"])
        request_copy["sales_contact"] = client.sales_contact.id

        if "payment_due" in request_copy.keys():
            check_date(request_copy["payment_due"])

        self.check_object_permissions(request, contract)
        serializer = ContractSerializer(contract, data=request_copy)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class EventViewSet(viewsets.ModelViewSet):
    """
    A ViewSet to list, create, retrieve and update events.
    """

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (
        IsAuthenticated,
        IsManagerOrSupportContact,
    )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = EventFilter

    def list(self, request):
        user = self.request.user
        queryset = Event.objects.all()
        if user.role == "sales":
            queryset = queryset.filter(client__sales_contact=user)
        elif user.role == "support":
            queryset = queryset.filter(support_contact=user)

        queryset = self.filter_queryset(queryset).order_by("event_date")
        serializer = EventSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        raise ContractMustBeSigned()

    def retrieve(self, request, pk=None):
        user = request.user
        event = get_object_or_404(Event, id=pk)
        queryset = Event.objects.filter(id=pk)
        if user.role == "sales":
            queryset = queryset.filter(client__sales_contact=user)
        elif user.role == "support":
            queryset = queryset.filter(support_contact=user)
        if event is not None and queryset.count() == 0:
            raise NotInChargeOfEvent()

        serializer = EventSerializer(event)
        return Response(serializer.data)

    def update(self, request, pk=None):
        user = request.user
        event = get_object_or_404(Event, id=pk)
        request_copy = request.data.copy()
        if user.role == "management":
            support_contact_id = request.data["support_contact"]
            support_contact = User.objects.filter(id=support_contact_id)
            support_contact = support_contact.first()
            if support_contact.role != "support":
                raise NotSupportMember()
            else:
                request_copy["client"] = event.client.id
        elif user.role == "support":
            request_copy.update({"client": event.client.id,
                                 "support_client": user.id})
            if event.event_over and "status" not in request_copy.keys():
                raise EventOver()

        if "event_date" in request_copy.keys():
            check_date(request_copy["event_date"])

        self.check_object_permissions(request, event)
        serializer = EventSerializer(event, data=request_copy)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        user = request.user
        event = get_object_or_404(Event, id=pk)
        if user.role == "support" and event.event_over:
            raise EventOver()
        self.check_object_permissions(request, event)
        self.perform_destroy(event)
        return Response(status=status.HTTP_204_NO_CONTENT)


class NoteViewSet(viewsets.ModelViewSet):
    """
    A ViewSet to list, retrieve and create notes.
    """

    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = (
        IsAuthenticated,
        IsManagerOrEventSupportContact,
    )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = NoteFilter

    def list(self, request, event_pk=None):
        user = request.user
        event = get_object_or_404(Event, id=event_pk)
        events = Event.objects.filter(id=event_pk)
        queryset = Note.objects.filter(event_id=event_pk)
        if user.role == "sales":
            events = events.filter(client__sales_contact=user)
            queryset = queryset.filter(event__client__sales_contact=user)
        elif user.role == "support":
            queryset = queryset.filter(event__support_contact=user)
            events = events.filter(support_contact=user)
        if event is not None and events.count() == 0:
            raise NotInChargeOfEvent()

        queryset = self.filter_queryset(queryset).order_by("id")
        serializer = NoteSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, event_pk=None, pk=None):
        user = request.user
        event = get_object_or_404(Event, id=event_pk)
        note = get_object_or_404(Note, id=pk, event_id=event_pk)
        queryset = Note.objects.filter(id=pk, event_id=event_pk)
        if user.role == "sales":
            queryset = queryset.filter(event__client__sales_contact=user)
        elif user.role == "support":
            queryset = queryset.filter(event__support_contact=user)
        if event is not None and queryset.count() == 0:
            raise NotInChargeOfEvent()

        serializer = NoteSerializer(note)
        return Response(serializer.data)

    def create(self, request, event_pk=None):
        user = request.user
        event = get_object_or_404(Event, id=event_pk)
        if user.role == "sales":
            raise CannotCreateNote()
        elif user.role == "support":
            queryset = Event.objects.filter(id=event_pk,
                                            support_contact=user)
            if event is not None and queryset.count() == 0:
                raise NotInChargeOfEvent()
            if event.event_over:
                raise EventOver()

        serializer = NoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(event=event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, event_pk=None, pk=None):
        user = request.user
        note = get_object_or_404(Note, event_id=event_pk,
                                 id=pk)
        request_copy = request.data.copy()
        if user.role == "support":
            if note.event.event_over:
                raise EventOver()

        self.check_object_permissions(request, note)
        serializer = NoteSerializer(note, data=request_copy)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, event_pk=None, pk=None):
        user = request.user
        note = get_object_or_404(Note, event_id=event_pk, id=pk)
        if user.role == "support":
            if note.event.event_over:
                raise EventOver()
        self.check_object_permissions(request, note)
        self.perform_destroy(note)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ModelViewSet):
    """
    A ViewSet to update users.
    """

    queryset = User.objects.all().order_by("username")
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsManager,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter

    def update(self, request, pk=None):
        updated_user = get_object_or_404(User, id=pk)
        if updated_user == request.user:
            serializer = UserSerializer(updated_user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            raise CannotUpdateProfile()
