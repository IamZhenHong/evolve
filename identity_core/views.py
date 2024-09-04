from django.shortcuts import render
import openai
import os
from dotenv import load_dotenv
# Create your views here.
load_dotenv()
openai.api_key = os.environ.get('openai_api_key')

def summarise(entry,prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an experienced People Reader that is able to deduce the key identity exhbiited by the person who wrote the journal entry."},
            {"role": "user", "content": entry},
            {"role": "assistant", "content": prompt},
        ],
        max_tokens=150,
        temperature=0.5,
    )
    summary = response.choices[0].message["content"].strip()
    return summary

def get_mood(entry):
    prompt = "Extract the mood exhibited by the writer in the form of a single noun, and nothing else."
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an experienced People Reader that is able to deduce the key mood exhibited by the person who wrote the journal entry."},
            {"role": "user", "content": entry},
            {"role": "assistant", "content": prompt},
        ],
        max_tokens=10,  # Limit the response length to encourage a single-word answer
        temperature=0.5,
    )
    
    mood = response.choices[0].message["content"].strip()
    return mood