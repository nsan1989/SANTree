from django.db import models


# license choices.
class licenseChoices(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    ASSIGNED = "ASSIGNED", "Assigned"
    AVAILABLE = "AVAILABLE", "Available"
    RENEWAL_DUE = "RENEWAL_DUE", "Renewal Due"
    EXPIRED = "EXPIRED", "Expired"
    REVOKED = "REVOKED", "Revoked"


# asset status
class assetChoices(models.TextChoices):
    AVAILABLE = "AVAILABALE", "Available"
    REQUESTED = "REQUESTED", "Requested"
    DEPLOYED = "DEPLOYED", "Deployed"
    ASSIGNED = "ASSIGNED", "Assigned"
    REPAIR = "REPAIR", "Repair"
    FAULTY = "FAULTY", "Faulty"
    WAITING = "WAITING", "Waiting"
    PANDING = "PANDING", "Panding"
