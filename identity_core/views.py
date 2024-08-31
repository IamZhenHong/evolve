from django.shortcuts import render
import openai
import os
from dotenv import load_dotenv
from django.shortcuts import get_object_or_404
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from journal.models import JournalEntry
# Create your views here.
load_dotenv()
openai.api_key = os.environ.get('openai_api_key')

def summarise(entry,prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an advanced assistant that specializes in analyzing text to extract key identities and merging identity templates while eliminating duplicates. You understand the importance of precise language and will output identities in the form of pronouns or nouns, ensuring clarity and accuracy."},
            {"role": "user", "content": entry},
            {"role": "assistant", "content": prompt},
        ],
        max_tokens=150,
        temperature=0.5,
    )
    summary = response.choices[0].message["content"].strip()
    return summary

def load_embedding(entry):
    # Convert the stored binary embedding back to a numpy array
    return np.frombuffer(entry.embedding, dtype=np.float32)

def find_similar_journals(entry, top_n=2):
    query_embedding = load_embedding(entry)
    entries = JournalEntry.objects.exclude(pk=entry.pk)  # Exclude the current entry
    similarities = []

    for other_entry in entries:
        other_embedding = load_embedding(other_entry)
        similarity = cosine_similarity([query_embedding], [other_embedding])[0][0]
        similarities.append((other_entry, similarity))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    return [entry for entry, _ in similarities[:top_n]]

def similar_journals_view(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk)
    similar_entries = find_similar_journals(entry)
    
    return render(request, 'identity_core/similar_journals.html', {'entry': entry, 'similar_entries': similar_entries})


def load_identity_embedding(identity):
    # Implement your logic to get the embedding for the given identity
    # This is a placeholder; replace it with your actual implementation
    return np.array(identity)  # Example placeholder, needs actual logic

def find_similar_journals_by_identity(identity, top_n=5):
    identity_embedding = load_identity_embedding(identity)
    entries = JournalEntry.objects.all()
    similarities = []

    for entry in entries:
        entry_embedding = load_embedding(entry)
        similarity = cosine_similarity([identity_embedding], [entry_embedding])[0][0]
        similarities.append((entry, similarity))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    return [entry for entry, _ in similarities[:top_n]]

def similar_journals_by_identity_view(request, identity):
    similar_entries = find_similar_journals_by_identity(identity)
    
    return render(request, 'identity_core/similar_journals_by_identity.html', {'identity': identity, 'similar_entries': similar_entries})