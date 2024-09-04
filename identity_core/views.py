from django.shortcuts import render
import openai
import os
from dotenv import load_dotenv
from django.http import JsonResponse
from journal.neo4j_config import Neo4jConnection
from py2neo import Graph
# Create your views here.
load_dotenv()
openai.api_key = os.environ.get('openai_api_key')

driver = Neo4jConnection.get_driver()
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


# views.py

def get_graph(request):
    # Get Neo4j driver
    driver = Neo4jConnection.get_driver()
    limit = int(request.GET.get('limit', 2))
    # Create a session
    with driver.session() as session:
        # Query all nodes and relationships
        query = """
        MATCH (n)-[r]->(m)
        RETURN n, r, m
        LIMIT $limit
        """
        result = session.run(query,limit=limit)

        nodes = []
        edges = []

        for record in result:
            start_node = record['n']
            relationship = record['r']
            end_node = record['m']

            # Add nodes
            nodes.append({
                'data': {'id': str(start_node.id), 'label': start_node.get('name', 'No Title')}
            })
            nodes.append({
                'data': {'id': str(end_node.id), 'label': end_node.get('name', 'No Title')}
            })

            # Add edges
            edges.append({
                'data': {
                    'id': f'{start_node.id}-{relationship.type}-{end_node.id}',
                    'source': str(start_node.id),
                    'target': str(end_node.id),
                    'label': relationship.type
                }
            })

    # Return JSON response
    return JsonResponse({'nodes': nodes, 'edges': edges})

def show_graph(request):
    return render(request, 'identity_core/graph.html')