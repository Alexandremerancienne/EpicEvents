from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from .models import Client, Contract, Event, Note
from .permissions import (
    IsManagerOrClientSalesContact,
    IsManagerOrContractSalesContact,
    IsManagerOrEventSupportContact,
    IsManager, IsManagerOrNoteEventSupportContact,
)
from .serializers import (
    ClientSerializer,
    ContractSerializer,
    EventSerializer,
    UserSerializer,
    SalesAndManagementContractSerializer,
    SalesClientSerializer,
    NoteSerializer, NotesSerializer, UpdateEventSerializer,
)
from .exceptions import (
    MissingCredentials,
    ClientNotFound,
    ContractNotFound,
    EventNotFound,
    NotInChargeOfClient,
    NotInChargeOfContract,
    NotInChargeOfEvent,
    NoContractForClient,
    ContractNotSigned,
    NotSalesMember,
    ContractAlreadyExists, NotSupportMember,
)


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = (
        IsAuthenticated,
        IsManagerOrClientSalesContact,
    )

    def get_serializer_class(self):
        if self.request.user.role in ["management", "support"]:
            return ClientSerializer
        elif self.request.user.role == "sales":
            return SalesClientSerializer

    def list(self, request):
        user = self.request.user
        if user.role == "management":
            queryset = Client.objects.all().order_by("last_name")
        elif user.role == "sales":
            queryset = Client.objects.filter(sales_contact=user).order_by("last_name")
        elif user.role == "support":
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
        if user.role == "management":
            queryset = Client.objects.filter(id=pk)
            if queryset.count() == 0:
                raise ClientNotFound()
        elif user.role == "sales":
            queryset = Client.objects.filter(id=pk, sales_contact=user)
            if client.count() == 0 and queryset.count() == 0:
                raise ClientNotFound()
            elif client.count() != 0 and queryset.count() == 0:
                raise NotInChargeOfClient()
        elif user.role == "support":
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

    def create(self, request):
        user = request.user
        if user.role == "management":
            sales_contact_field = request.data["sales_contact"]
            sales_contact = User.objects.filter(id=sales_contact_field, role="sales")
            if sales_contact.count() == 0:
                raise NotSalesMember()
            else:
                serializer = ClientSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
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
        if user.role == "management":
            sales_contact_field = request.data["sales_contact"]
            sales_contact = User.objects.filter(id=sales_contact_field, role="sales")
            if sales_contact.count() == 0:
                raise NotSalesMember()
        elif user.role == "sales":
            pass
        else:
            raise MissingCredentials()
        client = Client.objects.get(id=pk)
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

    def get_serializer_class(self):
        if self.request.user.role == "support":
            return ContractSerializer
        elif self.request.user.role in ["management", "sales"]:
            return SalesAndManagementContractSerializer

    def list(self, request):
        user = self.request.user
        if user.role == "management":
            queryset = Contract.objects.all().order_by("id")
        elif user.role == "sales":
            queryset = Contract.objects.filter(sales_contact=user).order_by("id")
        elif user.role == "support":
            raise MissingCredentials()
        else:
            raise MissingCredentials()
        serializer = ContractSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = request.user
        contract = Contract.objects.filter(id=pk)
        if user.role == "management":
            queryset = Contract.objects.filter(id=pk)
            if queryset.count() == 0:
                raise ContractNotFound()
        elif user.role == "sales":
            queryset = Contract.objects.filter(id=pk, sales_contact=user)
            if contract.count() == 0 and queryset.count() == 0:
                raise ContractNotFound()
            elif contract.count() != 0 and queryset.count() == 0:
                raise NotInChargeOfContract()
        elif user.role == "support":
            raise NotInChargeOfContract()
        else:
            raise MissingCredentials()

        retrieved_contract = queryset.first()
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
            serializer = ContractSerializer(data=request_copy)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif user.role == "sales":
            request_copy = request.data.copy()
            request_copy["sales_contact"] = user.id

            user_clients = Client.objects.filter(sales_contact=request.user.id)
            clients_id = [client.id for client in user_clients]

            if int(request_copy["client"]) in clients_id:
                serializer = ContractSerializer(data=request_copy)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                raise NotInChargeOfClient()
        else:
            raise MissingCredentials()

    def update(self, request, pk=None):
        user = request.user
        if user.role in ["management", "sales"]:
            contract = Contract.objects.get(id=pk)
            request_copy = request.data.copy()
            request_copy["client"] = contract.client.id
            request_copy["sales_contact"] = contract.sales_contact.id
            self.check_object_permissions(request, contract)
            serializer = ContractSerializer(contract, data=request_copy)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            raise MissingCredentials()


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (
        IsAuthenticated,
        IsManagerOrEventSupportContact,
    )

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return UpdateEventSerializer
        else:
            return EventSerializer

    def list(self, request):
        user = self.request.user
        if user.role == "management":
            queryset = Event.objects.all().order_by("id")
        elif user.role == "sales":
            queryset = Event.objects.filter(client__sales_contact=user).order_by("id")
        elif user.role == "support":
            queryset = Event.objects.filter(support_contact=user).order_by("id")
        else:
            raise MissingCredentials()
        serializer = EventSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = request.user
        event = Event.objects.filter(id=pk)
        if user.role == "management":
            queryset = Event.objects.filter(id=pk)
            if queryset.count() == 0:
                raise EventNotFound()
        elif user.role == "sales":
            queryset = Event.objects.filter(id=pk, client__sales_contact=user)
            if event.count() == 0 and queryset.count() == 0:
                raise EventNotFound()
            elif event.count() != 0 and queryset.count() == 0:
                raise NotInChargeOfEvent()
        elif user.role == "support":
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

    def create(self, request, pk=None):
        user = request.user
        if user.role == "management":
            request_copy = request.data.copy()
            event_client = int(request_copy["client"])
            client_contract = Contract.objects.filter(client=event_client)
            if client_contract.count() == 0:
                raise NoContractForClient()
            else:
                contract = client_contract.first()
                if contract.status is False:
                    raise ContractNotSigned()
                else:
                    support_contact_id = request.data["support_contact"]
                    support_contact = User.objects.filter(id=support_contact_id)
                    support_contact = support_contact.first()
                    if support_contact.role != "support":
                        raise NotSupportMember()
                    else:
                        serializer = EventSerializer(data=request.data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif user.role == "sales":
            request_copy = request.data.copy()
            event_client = int(request_copy["client"])
            client_contract = Contract.objects.filter(client=event_client)
            if client_contract.count() == 0:
                raise NoContractForClient()
            else:
                contract = client_contract.first()
                if contract.status is False:
                    raise ContractNotSigned()
                else:
                    user_clients = Client.objects.filter(sales_contact=request.user.id)
                    clients_id = [client.id for client in user_clients]
                    if int(request_copy["client"]) in clients_id:
                        serializer = EventSerializer(data=request_copy)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    else:
                        raise NotInChargeOfClient()
        else:
            raise MissingCredentials()

    def update(self, request, pk=None):
        user = request.user
        if user.role == "management":
            support_contact_id = request.data["support_contact"]
            support_contact = User.objects.filter(id=support_contact_id)
            support_contact = support_contact.first()
            if support_contact.role != "support":
                raise NotSupportMember()
            else:
                request_copy = request.data.copy()
                event = Event.objects.get(id=pk)
                request_copy["client"] = event.client.id
                self.check_object_permissions(request, event)
                serializer = EventSerializer(event, data=request_copy)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (
        IsAuthenticated,
        IsManager,
    )

    def list(self, request):
        user = self.request.user
        if user.role == "management":
            queryset = User.objects.all().order_by("username")
            serializer = UserSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            raise MissingCredentials()

    def retrieve(self, request, pk=None):
        user = request.user
        if user.role == "management":
            queryset = User.objects.filter(id=pk)
            retrieved_user = queryset.first()
            serializer = UserSerializer(retrieved_user)
            return Response(serializer.data)
        else:
            raise MissingCredentials()

    def create(self, request, pk=None):
        user = request.user
        if user.role == "management":
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise MissingCredentials()


class NotesViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = (IsAuthenticated,
                          IsManagerOrNoteEventSupportContact,)

    def get_serializer_class(self):
        if self.request.user.role in ["management", "support"]:
            return NotesSerializer

    def list(self, request, event_pk=None):
        user = request.user
        if user.role == "management":
            queryset = Note.objects.filter(event_id=event_pk).order_by("id")
        elif user.role == "support":
            queryset = Note.objects.filter(event__support_contact=user)
            if queryset.count() == 0:
                raise NotInChargeOfEvent()
            else:
                queryset = Note.objects.filter(event_id=event_pk).order_by("id")
        elif user.role == "sales":
            queryset = Note.objects.filter(event_id=event_pk,
                                           event__client__sales_contact=user).order_by("id")
            if queryset.count() == 0:
                raise NotInChargeOfEvent()
        serializer = NoteSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, event_pk=None, pk=None):
        user = request.user
        if user.role == "management":
            queryset = Note.objects.filter(id=pk, event_id=event_pk)
        elif user.role == "support":
            queryset = Note.objects.filter(event__support_contact=user)
            if queryset.count() == 0:
                raise NotInChargeOfEvent()
            else:
                queryset = Note.objects.filter(id=pk, event_id=event_pk)
        elif user.role == "sales":
            queryset = Note.objects.filter(id=pk, event_id=event_pk,
                                           event__client__sales_contact=user)
            if queryset.count() == 0:
                raise NotInChargeOfEvent()
        serializer = NoteSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, event_pk=None):
        user = request.user
        if user.role in ["management", "support"]:
            event = get_object_or_404(Event, id=event_pk)
            print("EVENT", event)
            request_copy = request.data.copy()
            request_copy["event"] = event.id
            print("REQUEST COPY", request_copy)
            serializer = NoteSerializer(data=request_copy)
            print(serializer)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise MissingCredentials()
