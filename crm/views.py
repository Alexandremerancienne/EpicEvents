from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework.decorators import action

from accounts.models import User
from .models import Client, Contract, Event, Note
from .permissions import (
    IsManagerOrClientSalesContact,
    IsManagerOrContractSalesContact,
    IsManagerOrEventSupportContact,
    IsManager,
)
from .serializers import (
    ClientSerializer,
    ContractSerializer,
    EventSerializer,
    UserSerializer,
    SalesContractSerializer,
    SalesClientSerializer,
)
from .exceptions import (
    MissingCredentials,
    ClientNotFound,
    ContractNotFound,
    EventNotFound,
    NotInChargeOfClient,
    NotInChargeOfContract,
    NotInChargeOfEvent,
    ClientAttributionError,
    NoContractForClient,
    ContractNotSigned,
    NotSalesMember,
    NoExistingContractBetweenSellerAndClient,
    ContractAlreadyExists,
    ContractAlreadyExistsWithAnotherSeller,
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
            queryset = Client.objects.all()
        elif user.role == "sales":
            queryset = Client.objects.filter(sales_contact=user)
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

    def create(self, request, pk=None):
        user = request.user
        if user.role == "management":
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


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = (
        IsAuthenticated,
        IsManagerOrContractSalesContact,
    )

    def get_serializer_class(self):
        if self.request.user.role in ["management", "support"]:
            return ContractSerializer
        elif self.request.user.role == "sales":
            return SalesContractSerializer

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
            sales_contact = get_object_or_404(
                User, id=int(request.data["sales_contact"])
            )
            client = get_object_or_404(Client, id=int(request.data["client"]))
            if sales_contact.role != "sales":
                raise NotSalesMember()
            else:
                if client.sales_contact.id != int(request.data["sales_contact"]):
                    raise NotInChargeOfClient()
                else:
                    contract = Contract.objects.filter(
                        client=client, sales_contact=sales_contact
                    )
                    if contract.count() != 0:
                        raise ContractAlreadyExists()
                    else:
                        serializer = ContractSerializer(data=request.data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif user.role == "sales":
            client = get_object_or_404(Client, id=int(request.data["client"]))
            contract = Contract.objects.filter(client=client, sales_contact=user)
            if contract.count() != 0:
                raise ContractAlreadyExists()
            else:
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


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (
        IsAuthenticated,
        IsManagerOrEventSupportContact,
    )
    #
    # @action(methods=["get"], detail=True)
    # def notes(self, request, pk=None):
    #     data = Note.objects.all()
    #     return Response(data=data)

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
                if contract.status is True:
                    serializer = EventSerializer(data=request.data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    raise ContractNotSigned()
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
            queryset = User.objects.all().order_by("id")
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
