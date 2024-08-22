from django.shortcuts import render
import openai
import os
# Create your views here.

openai.api_key = os.environ.get('OPENAI_API_KEY')

def summarise(entry):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant that summarizes content."},
            {"role": "user", "content": entry},
            {"role": "assistant", "content": "Please summarize the key identity exhibited in the entry."}
        ],
        max_tokens=150,
        temperature=0.5,
    )
    summary = response.choices[0].message["content"].strip()
    return summary