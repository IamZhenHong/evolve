from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import JournalEntry
from .forms import JournalEntryForm  # Assuming a form for creating/editing


def list(request):
    # entries = JournalEntry.objects.filter(user=request.user)
    return render(request, 'journal/list.html')

def detail(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk)
    return render(request, 'journal/detail.html', {'entry': entry})

def create(request):
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect('list')  # Replace with your desired redirect URL
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
    return redirect('list')