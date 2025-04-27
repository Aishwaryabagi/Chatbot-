import os
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Job search API configuration (using RapidAPI for JobSearchAPI)
JOB_API_KEY = os.getenv('670d0f353bmsh97a721bf232e99dp18226fjsn406a2e0d93b1')
JOB_API_HOST = "jsearch.p.rapidapi.com"

# Initialize system message for career focus
SYSTEM_MESSAGE = """
You are CareerAssist, a specialized AI assistant that only answers questions related to jobs, careers, 
professional development, resume writing, interview preparation, and job searching.

If a user asks a question that is not related to careers or professional topics, politely inform them 
that you can only provide information about career-related topics.

When providing advice, use current job market knowledge and best practices in career development.
"""

# Message history storage (in production, use a proper database)
conversation_history = {}

@app.route('/')
def home():
    return render_template('index.html')

def is_career_related(query):
    """Check if the query is related to careers using the LLM"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You determine if a query is related to jobs, careers, professional development, job searching, interviews, resumes, or workplace issues. Respond with only 'yes' or 'no'."},
            {"role": "user", "content": f"Is this query related to jobs, careers, or professional development? Query: '{query}'"}
        ],
        max_tokens=10
    )
    answer = response.choices[0].message.content.strip().lower()
    return answer == "yes"

def search_job_listings(query, location="", limit=5):
    """Fetch real-time job listings using JobSearch API"""
    url = "jsearch.p.rapidapi.com"
    
    querystring = {
        "query": query,
        "page": "1",
        "num_pages": "1",
        "date_posted": "month"
    }
    
    if location:
        querystring["location"] = location
    
    headers = {
        "X-RapidAPI-Key": JOB_API_KEY,
        "X-RapidAPI-Host": JOB_API_HOST
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        jobs = response.json().get('data', [])
        
        # Format job results
        results = []
        for job in jobs[:limit]:
            results.append({
                "title": job.get('job_title'),
                "company": job.get('employer_name'),
                "location": job.get('job_city', '') + ", " + job.get('job_country', ''),
                "link": job.get('job_apply_link'),
                "date_posted": job.get('job_posted_at_datetime_utc')
            })
        return results
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []

def get_salary_data(job_title, location=""):
    """Fetch salary data for a job title"""
    url = "https://jsearch.p.rapidapi.com/estimated-salary"
    
    querystring = {"job_title": job_title, "location": location, "radius": "100"}
    
    headers = {
        "X-RapidAPI-Key": JOB_API_KEY,
        "X-RapidAPI-Host": JOB_API_HOST
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json().get('data', [{}])[0]
        return {
            "min_salary": data.get('min_salary'),
            "max_salary": data.get('max_salary'),
            "median_salary": data.get('median_salary'),
            "currency": data.get('salary_currency')
        }
    except Exception as e:
        print(f"Error fetching salary data: {e}")
        return {}

def get_career_advice(query, user_id):
    """Get advice from the LLM using conversation history"""
    # Retrieve conversation history
    messages = conversation_history.get(user_id, [])
    
    # Add system message at the start
    if not messages:
        messages.append({"role": "system", "content": SYSTEM_MESSAGE})
    
    # Add user query
    messages.append({"role": "user", "content": query})
    
    # Get response from the LLM
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        max_tokens=1000
    )
    
    assistant_response = response.choices[0].message.content
    
    # Update conversation history
    messages.append({"role": "assistant", "content": assistant_response})
    
    # Keep only last 10 messages to manage token usage
    if len(messages) > 12:  # system + 10 conversation turns
        messages = [messages[0]] + messages[-10:]
    
    conversation_history[user_id] = messages
    
    return assistant_response

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get('message', '')
    user_id = data.get('user_id', 'default_user')
    location = data.get('location', '')
    
    # Check if query is career-related
    if not is_career_related(query):
        return jsonify({
            "response": "I can only answer questions related to jobs, careers, and professional development. Please ask me something about job searching, resume writing, interviews, career growth, or workplace skills."
        })
    
    # Determine if we need real-time job data
    needs_job_listings = any(keyword in query.lower() for keyword in ['job listings', 'job openings', 'find jobs', 'search jobs', 'open positions'])
    needs_salary_data = any(keyword in query.lower() for keyword in ['salary', 'pay', 'compensation', 'earn', 'income'])
    
    # Get job listings if needed
    job_data = None
    if needs_job_listings:
        job_search_terms = query.lower().replace('job listings', '').replace('job openings', '').replace('find jobs', '').replace('search jobs', '').strip()
        job_data = search_job_listings(job_search_terms, location)
    
    # Get salary data if needed
    salary_data = None
    if needs_salary_data:
        # Extract job title from query - in production, use NLP for better extraction
        job_title = query.lower().replace('salary', '').replace('pay', '').replace('compensation', '').replace('earn', '').replace('income', '').strip()
        salary_data = get_salary_data(job_title, location)
    
    # Enhance query with real-time data if available
    enhanced_query = query
    
    if job_data:
        job_info = "\n\nHere's real-time job information to incorporate in your response:\n"
        for i, job in enumerate(job_data):
            job_info += f"{i+1}. {job['title']} at {job['company']} in {job['location']}\n"
        enhanced_query += job_info
    
    if salary_data and salary_data.get('median_salary'):
        salary_info = f"\n\nIncorporate this salary data in your response: {salary_data['job_title']} typically earns between {salary_data['min_salary']}-{salary_data['max_salary']} {salary_data['currency']} with a median of {salary_data['median_salary']} {salary_data['currency']}."
        enhanced_query += salary_info
    
    # Get advice from the LLM
    response = get_career_advice(enhanced_query, user_id)
    
    return jsonify({
        "response": response,
        "job_data": job_data if job_data else None,
        "salary_data": salary_data if salary_data else None
    })

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    data = request.json
    user_id = data.get('user_id', 'default_user')
    
    if user_id in conversation_history:
        # Keep only the system message
        system_message = conversation_history[user_id][0] if conversation_history[user_id] else {"role": "system", "content": SYSTEM_MESSAGE}
        conversation_history[user_id] = [system_message]
    
    return jsonify({"status": "conversation reset"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)