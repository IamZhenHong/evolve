from django.shortcuts import render
import openai
import os
from dotenv import load_dotenv
from django.http import JsonResponse
from journal.neo4j_config import Neo4jConnection
from py2neo import Graph
from neo4j import GraphDatabase
from pandas import DataFrame
import json
from .models import CommunitySummary
# from neo4j_graph_data_science import GraphDataScience as gds  # Import the GDS library

# Create your views here.
load_dotenv()

from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()


# Define the project and secret information
project_id = "empyrean-button-434915-s8"
secret_id = "evolve"
secret_version = "latest"

# Build the secret version resource name
secret_version_name = f"projects/{project_id}/secrets/{secret_id}/versions/{secret_version}"

# Access the secret version
response = client.access_secret_version(name=secret_version_name)

# Extract the secret payload
secret_payload = response.payload.data.decode("UTF-8")

# Debug: print secret payload to verify contents
print("Secret payload:", secret_payload)

# Split the secret payload into environment variables
secret_lines = secret_payload.split('\n')
secrets = {}
for line in secret_lines:
    if '=' in line:
        key, value = line.split('=', 1)
        secrets[key.strip()] = value.strip().strip('"')  # Strips whitespace and surrounding quotes

# Debug: print extracted secrets to verify
print("Extracted secrets:", secrets)

# Retrieve and set OpenAI API key
api_key = secrets.get("openai_api_key")
if api_key:
    openai.api_key = api_key
    print("OpenAI API key set successfully.")
else:
    print("Failed to retrieve OpenAI API key from secrets.")

neo4j_uri = secrets.get("NEO4J_URI")
driver = Neo4jConnection.get_driver()


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

def community_summary(request):

    existing_communities = CommunitySummary.objects.first()

    if existing_communities:
        return render(request, 'identity_core/community.html', {
            'communities': existing_communities.communities
        })

    with driver.session() as session:
        # Execute the Cypher query
        result = session.run("""
            MATCH (n)-[r]->(m)
            WHERE n.community IS NOT NULL AND m.community IS NOT NULL AND n.community = m.community
            WITH n.community AS community, collect(n) AS nodes, collect(r) AS relationships
            RETURN community, nodes, relationships
            ORDER BY community;

        """)

        # Initialize a list to store community summaries
        communities = []

        # Process the result
        for record in result:
            community_id = record['community']
            nodes = record['nodes']
            relationships = record['relationships']
            
            # Summarize the nodes
            node_summary = []
            for node in nodes:

                # Access node properties using node.get('property_name') method
                summary = node.get('summary')  # Replace 'summary' with the actual property name if it's different
                if summary is not None:
                    node_summary.append({
                        'summary': summary,
                    })


            # Summarize the relationships
            relationship_summary = []
            for rel in relationships:
                relationship_summary.append({
                    'start': rel.start_node.id,
                    'end': rel.end_node.id,
                    'type': rel.type,
    
                })
            
            # Add the community summary
            communities.append({
                'community': community_id,
                'node_count': len(nodes),
                'relationship_count': len(relationships),
                'nodes': node_summary,
                'relationships': relationship_summary
            })
        for community in communities:
            community_summary_input = (
            f"Node Summary:\n{community['nodes']}\n\n"
            f"Relationship Summary:\n{community['relationships']}\n\n"
            "Please provide a comprehensive summary that highlights key emotional and event-related themes within this community."
        )
            response = openai.ChatCompletion.create(
            
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a summarization assistant focused on capturing the emotional and event landscape from journal entries by a single user and associated moods."},
                    {"role": "user", "content": community_summary_input},
                    {"role": "assistant", "content": "Provide a summary highlighting the key emotional and event-related themes within these journal entries by a single user and their moods.Be elaborate"}  
                ],
                max_tokens=150,
                temperature=0.5,
            )
            print(response.choices[0].message["content"].strip())
            community['summary'] = response.choices[0].message["content"].strip()
        
    
    
    CommunitySummary.objects.create(communities=communities)
    # Pass the community summaries to the template
    return render(request, 'identity_core/community.html', {
        'communities': communities
    })


def get_mood(entry):
    prompt = (
        "Extract all the distinct moods or emotions exhibited by the writer from the journal entry. "
        "List them as separate words, and ensure there are no duplicates. "
        "Provide the list in a comma-separated format."
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an experienced People Reader who can deduce the key moods or emotions exhibited by the person who wrote the journal entry."},
            {"role": "user", "content": entry},
            {"role": "assistant", "content": prompt},
        ],
        max_tokens=50,  # Increased token limit to accommodate multiple words
        temperature=0.5,
    )
    
    # Extract the response and split it into a list
    mood_list = response.choices[0].message["content"].strip()
    
    # Split the list by commas and remove any extra whitespace
    moods = [mood.strip() for mood in mood_list.split(',') if mood.strip()]
    
    # Remove duplicates by converting the list to a set and back to a list
    unique_moods = list(set(moods))
    
    return unique_moods


# views.py

def get_graph(request):
    # Get the Neo4j driver instance
    driver = Neo4jConnection.get_driver()
    limit = int(request.GET.get('limit', 10))

    def fetch_data(tx, limit):
        # Write your Cypher query to fetch nodes and relationships
        query = """
        MATCH (n)-[r]->(m)
        RETURN n, r, m
        LIMIT $limit
        """
        result = tx.run(query, limit=limit)
        nodes = {}
        edges = []

        for record in result:
            n = record["n"]
            m = record["m"]
            r = record["r"]

            # Determine the node type and set label accordingly
            if "JournalEntry" in n.labels:
                n_label = n.get("summary") or "No Summary"
            elif "User" in n.labels:
                n_label = "You  "
            elif "Mood" in n.labels:
                n_label = n.get("name") or "No Mood"
            else:
                n_label = n.get("title") or n.get("name") or "No Label"
                
            if "JournalEntry" in m.labels:
                m_label = m.get("summary") or "No Summary"
            elif "User" in m.labels:
                m_label = m.get("user_id") or "No User ID"
            elif "Mood" in m.labels:
                m_label = m.get("name") or "No Mood"
            else:
                m_label = m.get("title") or m.get("name") or "No Label"

            # Add nodes with appropriate label
            if n.id not in nodes:
                nodes[n.id] = {
                    "data": {
                        "id": n.id,
                        "label": n_label
                    }
                }
            if m.id not in nodes:
                nodes[m.id] = {
                    "data": {
                        "id": m.id,
                        "label": m_label
                    }
                }

            # Add edge
            edges.append({
                "data": {
                    "source": n.id,
                    "target": m.id,
                    "relationship": r.type
                }
            })

        # Convert nodes dictionary to a list
        nodes_list = list(nodes.values())

        return {"nodes": nodes_list, "edges": edges}

    with driver.session() as session:
        graph_data = session.execute_read(fetch_data, limit=limit)

    print(graph_data)  # For debugging purposes
    return JsonResponse(graph_data)

def show_graph(request):
    return render(request, 'identity_core/graph.html')



def project_graph(driver):
    with driver.session() as session:
        result = session.write_transaction(lambda tx: gds.graph.project(
            "communities",  # Graph name
            "*",  # Node projection for all nodes
            {
                "_ALL_": {
                    "type": "*",
                    "orientation": "UNDIRECTED",
                    "properties": {"weight": {"property": "*", "aggregation": "COUNT"}},
                }
            },
        ))
        return result

def run_community_detection(driver):
    with driver.session() as session:
        community_result = session.read_transaction(lambda tx: gds.louvain.stream("communities"))
        communities = []
        for record in community_result:
            communities.append({"nodeId": record['nodeId'], "communityId": record['communityId']})
        return communities

def graph_view(request):
    # Get the Neo4j driver instance
    driver = Neo4jConnection.get_driver()

    # Project the graph
    project_graph(driver)

    # Run community detection
    communities = run_community_detection(driver)

    # Prepare data for rendering
    context = {
        "communities": communities,
    }

    # Render the template
    return render(request, 'graph_view.html', context)

def graph_data(request):
    # Get the Neo4j driver instance
    driver = Neo4jConnection.get_driver()

    # Return graph data in JSON format
    with driver.session() as session:
        result = session.read_transaction(lambda tx: gds.graph.read("communities"))
    return JsonResponse(result)
