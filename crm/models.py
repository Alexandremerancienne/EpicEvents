from django.db import models
from django.conf import settings


class Client(models.Model):

    objects = None
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20)
    company = models.CharField(max_length=250)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    sales_contact = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return (
            f"{self.first_name} {self.last_name} "
            f"({self.company}) - Sales contact : {self.sales_contact}"
        )


class Contract(models.Model):

    sales_contact = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    client = models.ForeignKey(to=Client, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)
    amount = models.FloatField()
    payment_due = models.DateTimeField()

    def __str__(self):
        return f"{self.client} - contract n°{self.pk}"


class Event(models.Model):

    client = models.ForeignKey(to=Client, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    support_contact = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    event_over = models.BooleanField(default=False)
    attendees = models.IntegerField()
    event_date = models.DateTimeField(null=True)

    def __str__(self):
        return f"Event {self.client.company} ({self.event_date})"


class Note(models.Model):

    description = models.TextField()
    event = models.ForeignKey(to=Event, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"Event: {self.description}"
