from rest_framework import serializers

from accounts.models import User

from .models import Client, Contract, Event, Note


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for the list of clients."""

    class Meta:
        model = Client
        exclude = ("date_created", "date_updated")


class ContractSerializer(serializers.ModelSerializer):
    """Serializer for the list of contracts."""
    class Meta:
        model = Contract
        exclude = ("date_created", "date_updated")


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""

    class Meta:
        model = User
        fields = ["id", "username", "role", "password"]
        extra_kwargs = {"password": {"write_only": True}}

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
        fields = ["id", "description"]


class EventSerializer(serializers.ModelSerializer):
    """Serializer for the list of events."""

    class Meta:
        model = Event
        exclude = ("date_created", "date_updated")
