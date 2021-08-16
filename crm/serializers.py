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
        fields = "__all__"


class SalesAndManagementContractSerializer(serializers.ModelSerializer):
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


class UpdateEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        exclude = ("client",)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password", "role"]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        exclude = ("event",)


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"
