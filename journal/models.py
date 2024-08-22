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
    embedding = models.BinaryField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Generate embedding before saving
        self.embedding = self.generate_embedding()
        super().save(*args, **kwargs)

    def generate_embedding(self):
        model_name = "distilbert-base-uncased"  # Use your preferred model
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)

        inputs = tokenizer(self.content, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Take the mean of the last hidden state to create a fixed-size embedding
        embedding = outputs.last_hidden_state.mean(dim=1).numpy()
        return embedding.tobytes()  # Convert to binary for storage

