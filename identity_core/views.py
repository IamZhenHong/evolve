from django.shortcuts import render
import openai
import os
from dotenv import load_dotenv
from django.http import JsonResponse
from journal.neo4j_config import Neo4jConnection
from py2neo import Graph
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
                n_label = n.get("user_id") or "No User ID"
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
