from django.db import models
from accounts.models import CustomUsers
from webpush.models import SubscriptionInfo as BaseSubscriptionInfo

# Subscription Info Model.
class PushSubscription(BaseSubscriptionInfo):
    user = models.ForeignKey(CustomUsers, on_delete=models.CASCADE, null=True, blank=True)
    endpoint_name = models.CharField(max_length=500, unique=True, default=None)

    def __str__(self):
        return f"{self.user} -> {self.endpoint_name}"
    