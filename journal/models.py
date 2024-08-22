from django.db import models
from django.conf import settings

class JournalEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ai_summary = models.CharField(max_length=100)
    content = models.TextField()
    # Image,date_updated
    date_created= models.DateTimeField(auto_now_add=True)
    key_characteristics = models.CharField(max_length=100)

