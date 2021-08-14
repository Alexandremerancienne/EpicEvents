from rest_framework import serializers

from .models import Client, Contract, Event

from accounts.models import User


class SalesClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        exclude = ("sales_contact",)


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"


class SalesContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        exclude = ("sales_contact",)


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password", "role"]
