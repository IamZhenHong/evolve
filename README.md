# Evolve

## **Features**

### Current Features:
1. **CRUD for Journal Entries**:
   - Users can **create**, **read**, **update**, and **delete** journal entries to reflect on their thoughts, goals, and progress.
   - Journaling is an integral part of the platform, allowing users to document their self-improvement journey.

2. **AI Summarization of Journal Entries**:
   - The app utilizes **AI-powered summarization** to condense long journal entries into key insights, helping users reflect on the most important aspects of their entries.
   - AI assists in understanding recurring themes and providing concise summaries for easier reflection.

3. **Community Detection (Graph Analysis)**:
   - By analyzing user interactions and shared goals, the platform identifies **community clusters** using graph-based analysis powered by the **Leiden algorithm**.
   - AI-powered summarization is then applied to these clusters, generating key insights that help users understand the dynamics of their community and the common themes driving personal development in their cluster.


---

## **Planned Features (Roadmap)**

1. **Goal Setting and Tracking**:
   - Users will be able to set personal goals and monitor their progress, with visual tools to track short- and long-term objectives.
   
2. **AI-Driven Insights and Recommendations**:
   - Enhanced AI insights that provide tailored feedback on user behavior, personal growth patterns, and habit formation.

3. **Habit Tracking**:
   - A habit tracking feature to encourage users to build consistent, healthy habits, with streaks and progress reminders.

4. **Guided Reflections and Prompts**:
   - Daily and weekly reflection prompts to guide users through introspection and deeper personal growth.

5. **Group Challenges and Social Accountability**:
   - Ability to join group challenges (e.g., fitness, mindfulness) for a sense of community and accountability.

6. **Gamification**:
   - Earn badges and rewards for hitting milestones, such as consistent journaling or completing challenges.

---

## **Tech Stack**

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, Boostrap
- **AI Integration**: OpenAI api
- **Graph Database**: Neo4j enterprise edition
- **Deployment**: GCP, dockers

---

## **Getting Started**
#### 1. Clone git repository
```bash
git clone "https://github.com/IamZhenHong/evolve.git"
```

#### 2. Setup virtual environment
```bash
# Install virtual environment
sudo pip install virtualenv

# Make a directory
mkdir envs

# Create virtual environment
virtualenv ./envs/

# Activate virtual environment
source envs/bin/activate
```

#### 3. Install requirements
```bash
cd evolve/
pip install -r requirements.txt
```

#### 4. Run the server
```bash
# Make migrations
python manage.py makemigrations
python manage.py migrate

# Run the server
python manage.py runserver 0:8001

# your server is up on port 8001
```
Try opening [http://localhost:8001](http://localhost:8001) in the browser.
Now you are good to go.
