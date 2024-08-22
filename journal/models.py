from django.db import models
from django.conf import settings

class JournalEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    summary= models.CharField(max_length=200, default="abc")
    cumulative_summary = models.TextField(default="abc")
    content = models.TextField()
    # Image,date_updated
    date_created= models.DateTimeField(auto_now_add=True)
    key_characteristics = models.CharField(max_length=100)

