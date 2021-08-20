from rest_framework import serializers

from .models import Client, Contract, Event, Note

from accounts.models import User


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for the list of clients."""

    class Meta:
        model = Client
        exclude = ("date_created", "date_updated")


class SalesClientSerializer(serializers.ModelSerializer):
    """Serializer for the list of clients as seen from a Sales account."""

    class Meta:
        model = Client
        exclude = ("sales_contact",)


class ContractSerializer(serializers.ModelSerializer):
    """Serializer for the list of contracts."""
    class Meta:
        model = Contract
        exclude = ("date_created", "date_updated")


class ManagementContractSerializer(serializers.ModelSerializer):
    """Serializer for the list of contracts as seen from a Management account."""

    class Meta:
        model = Contract
        exclude = (
            "sales_contact",
            "date_created",
            "date_updated",
        )


class SalesContractSerializer(serializers.ModelSerializer):
    """Serializer for the list of contracts as seen from a Sales account."""

    class Meta:
        model = Contract
        exclude = (
            "sales_contact",
            "date_created",
            "date_updated",
            "client",
        )


class EventSerializer(serializers.ModelSerializer):
    """Serializer for the list of events."""

    class Meta:
        model = Event
        exclude = ("date_created", "date_updated")


class SupportEventSerializer(serializers.ModelSerializer):
    """Serializer for the list of events as seen from a Support account."""

    class Meta:
        model = Event
        exclude = ("date_created", "date_updated", "support_contact", "client")


class ManagementEventSerializer(serializers.ModelSerializer):
    """Serializer for the list of events as seen from a Management account."""

    class Meta:
        model = Event
        exclude = (
            "date_created",
            "date_updated",
            "client",
        )


class GetUserSerializer(serializers.ModelSerializer):
    """Serializer for the list of users for GET requests."""

    class Meta:
        model = User
        fields = ["id", "username", "role"]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the list of users for POST and PUT requests."""

    class Meta:
        model = User
        fields = ["id", "username", "role", "password"]

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        instance.set_password(validated_data["password"])
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == "password":
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class NoteSerializer(serializers.ModelSerializer):
    """Serializer for the list of notes."""

    class Meta:
        model = Note
        fields = "__all__"


class ManagementAndSupportNoteSerializer(serializers.ModelSerializer):
    """Serializer for the list of events as seen from a Management account
    or a Support account."""

    class Meta:
        model = Note
        exclude = ("event",)
