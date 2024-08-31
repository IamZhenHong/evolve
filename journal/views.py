from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import JournalEntry
from .forms import JournalEntryForm  # Assuming a form for creating/editing
from identity_core.views import summarise

def list(request):
    entries = JournalEntry.objects.filter(user=request.user)
    return render(request, 'journal/list.html', {'entries': entries})

def detail(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk)
    return render(request, 'journal/detail.html', {'entry': entry})

def create(request):
    prompt1 = "Instruction: Extract the writer's key identity from the provided text. If the key identity is undetectable, infer the closest identity. Use one pronoun or noun. Example: Suppose the text provided is 'I often find myself analyzing situations and thinking deeply about life.' The key identity extracted might be 'Thinker.' Input Format: - Text: Provide a piece of text where the writer's key identity needs to be extracted. - Prompt: 'Extract the writer's key identity. If undetectable, infer the closest. Use one pronoun or noun. Identity:' Output Format: - Identity: The most relevant pronoun or noun that represents the key identity of the writer."


    prompt2 = "Instruction: Merge two identity templates by removing duplicates. Output only the pronoun(s) or noun(s) representing the identities. Example: Suppose the two identities are 'Thinker' and 'Learner.' The merged output would be 'Thinker, Learner.' Input Format: - Identities: Provide two sets of identities to be merged. - Prompt: 'Merge two identity templates, removing duplicates. Output only the pronoun(s) or noun(s). Identity:, not the full sentence.'Output Format: - Identity: A single list of pronouns or nouns, with duplicates removed, from the provided identities."


    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            current_content = form.cleaned_data['content'][:100]  # Example of extracting summary
            current_summary = summarise(current_content,prompt1)
            cumulative_summary = ""
            last_entry = JournalEntry.objects.filter(user=request.user).order_by('-date_created').first()

            if last_entry:
                print(last_entry.cumulative_summary + "\n\n" + current_summary,prompt2)
                cumulative_summary = summarise(last_entry.cumulative_summary + "\n\n" + current_summary,prompt2)
            else:
                cumulative_summary = current_summary

            entry = form.save(commit=False)
            entry.summary = current_summary
            entry.cumulative_summary = cumulative_summary
            entry.user = request.user
            entry.save()

            return redirect('journal:list')  # Replace with your desired redirect URL
    else:
        form = JournalEntryForm()
    return render(request, 'journal/create.html', {'form': form})

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
def delete(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk)
    if request.user != entry.user:
        return HttpResponseForbidden()  # Or handle unauthorized access as needed
    entry.delete()
    return redirect('journal:list')