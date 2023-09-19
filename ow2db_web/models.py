from django.db import models


# Create your models here.
class Screenshot(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.BinaryField()
    sent_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"<Screenshot {self.id} by {self.sent_by} at {self.created_at}>"


class OW2UserImage(models.Model):
    id = models.AutoField(primary_key=True)
    original_sc = models.ForeignKey(
        Screenshot,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    image = models.BinaryField()
    histogram = models.BinaryField(blank=True, null=True)
    ow2_user = models.ForeignKey(
        "OW2UniqueUser",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        default=None,
    )


class OW2UniqueUser(models.Model):
    id = models.AutoField(primary_key=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=100, blank=True, null=True, unique=True)
    comment = models.TextField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
