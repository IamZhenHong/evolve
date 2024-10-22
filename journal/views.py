from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import JournalEntry
from .forms import JournalEntryForm  # Assuming a form for creating/editing
from identity_core.views import summarise, get_mood
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from neo4j.exceptions import ServiceUnavailable, AuthError
from .neo4j_config import Neo4jConnection
from .dao.entries import EntryDAO
from .dao.moods import MoodDAO
from datetime import datetime



driver = Neo4jConnection.get_driver()
entry_dao = EntryDAO(driver)
mood_dao = MoodDAO(driver)

@login_required
def list(request):
    print(request.user.id)
    entries = entry_dao.list_entries(request.user.id)
    print(entries)
    return render(request, 'journal/list.html', {'entries': entries})

@login_required
def detail(request, pk):
    entry = entry_dao.get_entry_by_id(pk)
    if (entry is None):
        print("Entry not found")
    return render(request, 'journal/detail.html', {'entry': entry})

@login_required
def create(request):
    prompt1 = "Instruction: Extract the writer's key identity from the provided text. If the key identity is undetectable, infer the closest identity. Use one pronoun or noun. Example: Suppose the text provided is 'I often find myself analyzing situations and thinking deeply about life.' The key identity extracted might be 'Thinker.' Input Format: - Text: Provide a piece of text where the writer's key identity needs to be extracted. - Prompt: 'Extract the writer's key identity. If undetectable, infer the closest. Use one pronoun or noun. Identity:' Output Format: - Identity: The most relevant pronoun or noun that represents the key identity of the writer."


    prompt2 = "Instruction: Merge two identity templates by removing duplicates. Output only the pronoun(s) or noun(s) representing the identities. Example: Suppose the two identities are 'Thinker' and 'Learner.' The merged output would be 'Thinker, Learner.' Input Format: - Identities: Provide two sets of identities to be merged. - Prompt: 'Merge two identity templates, removing duplicates. Output only the pronoun(s) or noun(s). Identity:, not the full sentence.'Output Format: - Identity: A single list of pronouns or nouns, with duplicates removed, from the provided identities."


    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            current_content = form.cleaned_data['content'][:100]
            print(current_content)
            current_summary = summarise(current_content, prompt1)
            cumulative_summary = ""
            last_entry = entry_dao.view_last_entry(request.user.id)
            if last_entry:
                cumulative_summary = summarise(last_entry[0]['entry'].get('cumulative_summary', '') + "\n\n" + current_summary, prompt2)
            else:
                cumulative_summary = current_summary

            current_date = datetime.now() 
            moods = get_mood(form.cleaned_data['content'])
    
            entry_dao.create_journal_entry(request.user.id, current_summary, cumulative_summary, form.cleaned_data['content'], current_date,moods)
            print('Entry created')

            return redirect('journal:list')
    else:
        form = JournalEntryForm()
        print("no post")
    
    
    return render(request, 'journal/create.html', {'form': form})

@login_required
def update(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk)
    if request.user != entry.user:
        return HttpResponseForbidden()  # Or handle unauthorized access as needed
    if request.method == 'POST':
        form = JournalEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('list')
    else:
        form = JournalEntryForm(instance=entry)
    return render(request, 'journal/update.html', {'form': form})

@login_required
def delete(request, node_id):
    entry_dao.delete_journal_entry(node_id)
    
    return redirect('journal:list') 




def check_neo4j_connection(request):
    try:
        # Get the driver instance
        driver = Neo4jConnection.get_driver()

        # Verify the connectivity
        with driver.session() as session:
            session.run("RETURN 1")
        
        # If successful, return a JSON response indicating success
        return JsonResponse({"status": "success", "message": "Connected to Neo4j database successfully!"})

    except (ServiceUnavailable, AuthError) as e:
        # If there's an error, return a JSON response indicating failure
        return JsonResponse({"status": "error", "message": f"Failed to connect to Neo4j database: {str(e)}"})

    except Exception as e:
        # Handle any other exceptions
        return JsonResponse({"status": "error", "message": f"An unexpected error occurred: {str(e)}"})

