from django.db import models

class CommunitySummary(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    communities = models.JSONField()  # This will store the serialized communities data
