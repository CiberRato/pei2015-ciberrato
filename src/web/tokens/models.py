from django.db import models
from authentication.models import Account
import binascii
import os


class UserToken(models.Model):
    """
    The default authorization token model.
    """
    key = models.CharField(max_length=40, primary_key=True)
    user = models.OneToOneField(Account, related_name='user_token')
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(UserToken, self).save(*args, **kwargs)

    @staticmethod
    def get_or_set(account):
        # token for stream
        if UserToken.objects.filter(user=account).count() == 1:
            t = UserToken.objects.get(user=account)
            t.delete()

        return UserToken.objects.create(user=account)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key