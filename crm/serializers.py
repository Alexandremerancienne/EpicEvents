from rest_framework import serializers

from .models import Client, Contract, Event, Note

from accounts.models import User


class SalesClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        exclude = ("sales_contact",)


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        exclude = ("date_created", "date_updated")


class ManagementContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        exclude = (
            "sales_contact",
            "date_created",
            "date_updated",
        )


class SalesContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        exclude = (
            "sales_contact",
            "date_created",
            "date_updated",
            "client",
        )


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        exclude = ("date_created",
                   "date_updated")


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        exclude = ("date_created", "date_updated")


class SupportEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        exclude = ("date_created", "date_updated",
                   "support_contact", "client")


class ManagementEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        exclude = ("date_created",
                   "date_updated",
                   "client",)


class UserSerializer(serializers.ModelSerializer):
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


class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "role"]


class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        exclude = ("event",)


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"
