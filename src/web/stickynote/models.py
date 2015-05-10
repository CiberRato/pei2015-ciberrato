from django.db import models
import uuid
from django.core.validators import MinLengthValidator


class StickyNote(models.Model):
    identifier = models.CharField(max_length=100, blank=False, unique=True, default=uuid.uuid4)

    active = models.BooleanField(default=False)
    time = models.IntegerField(default=5)
    note = models.CharField(max_length=150, validators=[MinLengthValidator(1)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        get_latest_by = "created_at"

    def __unicode__(self):
        return self.identifier