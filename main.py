from flask import Flask, render_template, jsonify
from dotenv import load_dotenv

load_dotenv()
import os
from supabase import create_client

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

app = Flask(__name__)
'''
# print all rows in jobs table with total quantity of jobs
#data = supabase.table("jobs").select("*", count='exact').execute()

# example of inserting a job into the table
#data = supabase.table("jobs").insert({"title": "Accountant"}).execute()

# example of updating an entry in jobs table job_id==2: location=remote, job_category="Information Technology"
#data = supabase.table("jobs").update({"location": "remote","category":"Information Technology"}).eq("id", 2).execute()

# print all rows in jobs table with only certain columns
data = supabase.table("jobs").select(
  "id, title, location, responsibilities, benefits", count='exact').execute()

result_data = data.data

print("\n")
for entry in result_data:
  print("ID:", entry['id'])
  print("Title:", entry['title'])
  print("Location:", entry['location'])
  print("Responsibilities:", entry.get('responsibilities', 'N/A'))
  print("Benefits:", entry.get('benefits', 'N/A'))
  print("\n")  # Empty line
'''

COMPANY = 'City of Williamston, Michigan'


def fetch_jobs_from_database():
  """
    Fetch jobs from the database using Supabase.
    """
  response = supabase.table("jobs").select(
    "id, title, location, responsibilities, benefits, category, salary",
    count='exact').execute()

  if hasattr(response, 'data') and 'error' in response.data:
    print("Error fetching data:", response.data['error'])
    return []

  # Format the salary for each job
  for job in response.data:
    if 'salary' in job and job['salary'] is not None:
      job['salary'] = format_salary(job['salary'])

  # Sort the jobs by their 'id' in ascending order
  sorted_jobs = sorted(response.data, key=lambda x: x['id'])

  return sorted_jobs


def format_salary(salary):
  try:
    # Convert salary to float and format it without cents
    formatted_salary = f"${float(salary):,.0f}"
    return formatted_salary
  except (ValueError, TypeError):
    # Return the original salary if there's an issue formatting
    return salary


@app.route("/")
def hello_world():
  jobs = fetch_jobs_from_database()
  return render_template('home.html', jobs=jobs, company_name=COMPANY)


@app.route("/api/jobs")
def job_list():
  jobs = fetch_jobs_from_database()
  return jsonify(jobs)


@app.route("/job-post-manager")
def jobs_table():
  return render_template('job-post-manager.html')


# script entry point
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))