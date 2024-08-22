from django.shortcuts import render
import openai
import os
from dotenv import load_dotenv
# Create your views here.
load_dotenv()
openai.api_key = os.environ.get('openai_api_key')

def summarise(entry):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant that summarizes content."},
            {"role": "user", "content": entry},
            {"role": "assistant", "content": "Please summarize the key identity exhibited in the entry.If you cannot detect any, just truthfully fill in not detected. Key identity:  Key beliefs: Key values: Key interests: Key goals: Key strengths: Key weaknesses: Key fears: Key needs: Key desires: Key motivations: Key roles: Key relationships: Key purpose: Key passions: Key identity statement: "},
        ],
        max_tokens=150,
        temperature=0.5,
    )
    summary = response.choices[0].message["content"].strip()
    return summary