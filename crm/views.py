from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from .filters import (
    ClientFilter,
    ContractFilter,
    EventFilter,
    UserFilter,
    NoteFilter
)
from .models import Client, Contract, Event, Note
from .permissions import (
    IsManagerOrClientSalesContact,
    IsManagerOrContractSalesContact,
    IsManagerOrEventSupportContact,
    IsManager,
    IsManagerOrNoteEventSupportContact,
)
from .serializers import (
    ClientSerializer,
    ContractSerializer,
    EventSerializer,
    UserSerializer,
    SalesClientSerializer,
    NoteSerializer,
    NotesSerializer,
    SupportEventSerializer,
    ManagementEventSerializer,
    GetUserSerializer,
    ManagementContractSerializer,
    SalesContractSerializer,
)
from .exceptions import (
    MissingCredentials,
    NotInChargeOfClient,
    NotInChargeOfContract,
    NotInChargeOfEvent,
    NotSalesMember,
    NotSupportMember,
    EventOver,
    ContractAlreadySigned,
    ContractMustBeSigned,
)

from django_filters import rest_framework as filters


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = (
        IsAuthenticated,
        IsManagerOrClientSalesContact,
    )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ClientFilter

    def get_serializer_class(self):
        if self.request.user.role in ["management", "support"]:
            return ClientSerializer
        elif self.request.user.role == "sales":
            return SalesClientSerializer

    def list(self, request):
        user = self.request.user
        if user.role == "management":
            queryset = Client.objects.all().order_by("last_name")
            queryset = self.filter_queryset(queryset)
        elif user.role == "sales":
            queryset = Client.objects.filter(sales_contact=user)
            queryset = queryset.order_by("last_name")
            queryset = self.filter_queryset(queryset)
        elif user.role == "support":
            followed_events = Event.objects.filter(support_contact=user)
            followed_events_clients =\
                [event.client.id for event in followed_events]
            queryset = Client.objects.filter(id__in=followed_events_clients)
            queryset = self.filter_queryset(queryset)
        else:
            raise MissingCredentials()

        serializer = ClientSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = request.user
        if user.role == "management":
            retrieved_client = get_object_or_404(Client, id=pk)
        elif user.role == "sales":
            queryset = Client.objects.filter(id=pk, sales_contact=user)
            retrieved_client = get_object_or_404(Client, id=pk)
            if retrieved_client is not None and queryset.count() == 0:
                raise NotInChargeOfClient()
        elif user.role == "support":
            followed_events = Event.objects.filter(support_contact=user)
            followed_events_clients =\
                [event.client.id for event in followed_events]
            queryset =\
                Client.objects.filter(id__in=followed_events_clients, id=pk)
            retrieved_client = get_object_or_404(Client, id=pk)
            if retrieved_client is not None and queryset.count() == 0:
                raise NotInChargeOfClient()

        serializer = ClientSerializer(retrieved_client)
        return Response(serializer.data)

    def create(self, request):
        user = request.user
        if user.role == "management":
            sales_contact_field = request.data["sales_contact"]
            sales_contact = User.objects.filter(id=sales_contact_field,
                                                role="sales")
            if sales_contact.count() == 0:
                raise NotSalesMember()
            else:
                serializer = ClientSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        elif user.role == "sales":
            request_copy = request.data.copy()
            request_copy["sales_contact"] = user.id
            serializer = ClientSerializer(data=request_copy)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise MissingCredentials()

    def update(self, request, pk=None):
        user = request.user
        client = get_object_or_404(Client, id=pk)
        if user.role == "management":
            sales_contact_field = request.data["sales_contact"]
            sales_contact =\
                User.objects.filter(id=sales_contact_field, role="sales")
            if sales_contact.count() == 0:
                raise NotSalesMember()
        elif user.role == "sales":
            pass
        else:
            raise MissingCredentials()

        self.check_object_permissions(request, client)
        serializer = ClientSerializer(client, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = (
        IsAuthenticated,
        IsManagerOrContractSalesContact,
    )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ContractFilter

    def get_serializer_class(self):
        if self.request.user.role == "support":
            return ContractSerializer
        elif self.request.user.role == "management":
            return ManagementContractSerializer
        elif self.request.user.role == "sales":
            return SalesContractSerializer

    def list(self, request):
        user = self.request.user
        if user.role == "management":
            queryset = Contract.objects.all().order_by("id")
            queryset = self.filter_queryset(queryset)
        elif user.role == "sales":
            queryset = Contract.objects.filter(sales_contact=user)
            queryset = queryset.order_by("id")
            self.filter_queryset(queryset)
        elif user.role == "support":
            raise MissingCredentials()
        else:
            raise MissingCredentials()

        serializer = ContractSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = request.user
        if user.role == "management":
            retrieved_contract = get_object_or_404(Contract, id=pk)
        elif user.role == "sales":
            queryset = Contract.objects.filter(id=pk, sales_contact=user)
            retrieved_contract = get_object_or_404(Contract, id=pk)
            if retrieved_contract is not None and queryset.count() == 0:
                raise NotInChargeOfContract()
        else:
            raise MissingCredentials()

        serializer = ContractSerializer(retrieved_contract)
        return Response(serializer.data)

    def create(self, request, pk=None):
        user = request.user
        if user.role == "management":
            request_copy = request.data.copy()
            form_client = request_copy["client"]
            client = Client.objects.filter(id=form_client)
            client = client.first()
            request_copy["sales_contact"] = client.sales_contact.id
            if "status" in request_copy.keys():
                new_event = Event(client=client, attendees=0)
                new_event.save()
            else:
                pass
            serializer = ContractSerializer(data=request_copy)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif user.role == "sales":
            request_copy = request.data.copy()
            form_client = request_copy["client"]
            client = Client.objects.filter(id=form_client)
            client = client.first()
            request_copy["sales_contact"] = user.id
            user_clients = Client.objects.filter(sales_contact=request.user.id)
            clients_id = [client.id for client in user_clients]
            if "status" in request_copy.keys():
                new_event = Event(client=client, attendees=0)
                new_event.save()
            else:
                pass
            if int(request_copy["client"]) in clients_id:
                serializer = ContractSerializer(data=request_copy)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            else:
                raise NotInChargeOfClient()
        else:
            raise MissingCredentials()

    def update(self, request, pk=None):
        user = request.user
        if user.role == "management":
            contract = get_object_or_404(Contract, id=pk)
            if contract.status:
                raise ContractAlreadySigned()
            else:
                request_copy = request.data.copy()
                if "status" in request_copy.keys():
                    new_event = Event(client=contract.client, attendees=0)
                    new_event.save()
                else:
                    form_client = request_copy["client"]
                    client = get_object_or_404(Client, id=form_client)
                    request_copy["sales_contact"] = client.sales_contact.id
        elif user.role == "sales":
            contract = get_object_or_404(Contract, id=pk)
            if contract.status:
                raise ContractAlreadySigned()
            else:
                request_copy = request.data.copy()
                if "status" in request_copy.keys():
                    new_event = Event(client=contract.client, attendees=0)
                    new_event.save()
                else:
                    request_copy["client"] = contract.client.id
                    client = get_object_or_404(Client,
                                               id=request_copy["client"])
                    request_copy["sales_contact"] = client.sales_contact.id
        else:
            raise MissingCredentials()

        self.check_object_permissions(request, contract)
        serializer = ContractSerializer(contract, data=request_copy)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (
        IsAuthenticated,
        IsManagerOrEventSupportContact,
    )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = EventFilter

    def get_serializer_class(self):
        if self.request.method == \
                "PUT" and self.request.user.role == "management":
            return ManagementEventSerializer
        elif self.request.method \
                == "PUT" and self.request.user.role == "support":
            return SupportEventSerializer
        else:
            return EventSerializer

    def list(self, request):
        user = self.request.user
        if user.role == "management":
            queryset = Event.objects.all().order_by("event_date")
            queryset = self.filter_queryset(queryset)
        elif user.role == "sales":
            queryset = Event.objects.filter(client__sales_contact=user)
            queryset = queryset.order_by("event_date")
            queryset = self.filter_queryset(queryset)
        elif user.role == "support":
            queryset = Event.objects.filter(support_contact=user)
            queryset = queryset.order_by("event_date")
            queryset = self.filter_queryset(queryset)
        else:
            raise MissingCredentials()

        serializer = EventSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        raise ContractMustBeSigned()

    def retrieve(self, request, pk=None):
        user = request.user
        if user.role == "management":
            retrieved_event = get_object_or_404(Event, id=pk)
        elif user.role == "sales":
            queryset = Event.objects.filter(id=pk, client__sales_contact=user)
            retrieved_event = get_object_or_404(Event, id=pk)
            if retrieved_event is not None and queryset.count() == 0:
                raise NotInChargeOfEvent()
        elif user.role == "support":
            queryset = Event.objects.filter(id=pk, support_contact=user)
            retrieved_event = get_object_or_404(Event, id=pk)
            if retrieved_event is not None and queryset.count() == 0:
                raise NotInChargeOfEvent()

        serializer = EventSerializer(retrieved_event)
        return Response(serializer.data)

    def update(self, request, pk=None):
        user = request.user
        event = get_object_or_404(Event, id=pk)
        if user.role == "management":
            support_contact_id = request.data["support_contact"]
            support_contact = User.objects.filter(id=support_contact_id)
            support_contact = support_contact.first()
            if support_contact.role != "support":
                raise NotSupportMember()
            else:
                request_copy = request.data.copy()
                request_copy["client"] = event.client.id
        elif user.role == "sales":
            raise MissingCredentials()
        elif user.role == "support":
            request_copy = request.data.copy()
            request_copy["client"] = event.client.id
            request_copy["support_client"] = user.id
            if not event.event_over and "status" in request_copy.keys():
                pass
            elif event.event_over and "status" not in request_copy.keys():
                raise EventOver()
            else:
                pass

        self.check_object_permissions(request, event)
        serializer = EventSerializer(event, data=request_copy)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class NotesViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = (
        IsAuthenticated,
        IsManagerOrNoteEventSupportContact,
    )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = NoteFilter

    def get_serializer_class(self):
        if self.request.user.role in ["management", "support"]:
            return NotesSerializer
        else:
            return NoteSerializer

    def list(self, request, event_pk=None):
        user = request.user
        if user.role == "management":
            queryset = Note.objects.filter(event_id=event_pk)
            queryset = queryset.order_by("id")
            queryset = self.filter_queryset(queryset)
        elif user.role == "support":
            queryset = Note.objects.filter(
                event_id=event_pk,
                event__support_contact=user
            )
            if queryset.count() == 0:
                raise NotInChargeOfEvent()
            else:
                queryset = Note.objects.filter(event_id=event_pk)
                queryset = queryset.order_by("id")
                queryset = self.filter_queryset(queryset)
        elif user.role == "sales":
            event = Event.objects.filter(id=event_pk,
                                         client__sales_contact=user)
            if event.count() == 0:
                raise NotInChargeOfEvent()
            else:
                queryset = Note.objects.filter(
                    event_id=event_pk,
                    event__client__sales_contact=user
                    )
                queryset = queryset.order_by("id")
                queryset = self.filter_queryset(queryset)

        serializer = NoteSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, event_pk=None, pk=None):
        user = request.user
        if user.role == "management":
            retrieved_note = get_object_or_404(Note, id=pk, event_id=event_pk)
        elif user.role == "support":
            queryset = Note.objects.filter(event__support_contact=user)
            retrieved_event = get_object_or_404(Event, id=event_pk)
            if queryset.count() == 0 and retrieved_event is not None:
                raise NotInChargeOfEvent()
            retrieved_note = get_object_or_404(Note, id=pk, event_id=event_pk)
        elif user.role == "sales":
            queryset = Note.objects.filter(
                id=pk, event_id=event_pk, event__client__sales_contact=user
            )
            retrieved_event = get_object_or_404(Event, id=event_pk)
            retrieved_note = get_object_or_404(Note, id=pk)
            if queryset.count() == 0 \
                    and retrieved_event is not None \
                    and retrieved_note is not None:
                raise NotInChargeOfEvent()

        serializer = NoteSerializer(retrieved_note)
        return Response(serializer.data)

    def create(self, request, event_pk=None):
        user = request.user
        if user.role == "management":
            event = get_object_or_404(Event, id=event_pk)
        elif user.role == "sales":
            raise MissingCredentials()
        elif user.role == "support":
            event = Event.objects.filter(id=event_pk, support_contact=user)
            if event.count() == 0:
                raise NotInChargeOfEvent()
            else:
                event = event.first()

        request_copy = request.data.copy()
        request_copy["event"] = event.id
        serializer = NoteSerializer(data=request_copy)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (
        IsAuthenticated,
        IsManager,
    )
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter

    def list(self, request):
        user = self.request.user
        if user.role == "management":
            queryset = User.objects.all().order_by("username")
            queryset = self.filter_queryset(queryset)
            serializer = GetUserSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            raise MissingCredentials()

    def retrieve(self, request, pk=None):
        user = request.user
        if user.role == "management":
            retrieved_user = get_object_or_404(User, id=pk)
            serializer = GetUserSerializer(retrieved_user)
            return Response(serializer.data)
        else:
            raise MissingCredentials()

    def create(self, request):
        user = request.user
        if user.role == "management":
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data = {
                "id": serializer.data["id"],
                "username": serializer.data["username"],
                "role": serializer.data["role"],
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            raise MissingCredentials()

    def update(self, request, pk=None):
        updated_user = get_object_or_404(User, id=pk)
        if updated_user == request.user:
            serializer = UserSerializer(updated_user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response_serializer = GetUserSerializer(updated_user,
                                                    data=request.data)
            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data)
        else:
            raise MissingCredentials()
