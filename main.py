from flask import Flask, render_template, jsonify
from dotenv import load_dotenv

load_dotenv()
import os
from supabase import create_client

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

app = Flask(__name__)

# print all rows in jobs table with total quantity of jobs
#data = supabase.table("jobs").select("*", count='exact').execute()

# example of inserting a job into the table
#data = supabase.table("jobs").insert({"title": "Accountant"}).execute()

# example of updating an entry in jobs table job_id==2: location=remote, job_category="Information Technology"
data = supabase.table("jobs").update({
  "location": "remote",
  "category": "Information Technology"
}).eq("id", 2).execute()

# print all rows in jobs table but only job_id, job_title, location columns, with total quantity of jobs
data = supabase.table("jobs").select("id, title, location",
                                     count='exact').execute()
print("\n", data, "\n")



COMPANY = 'City of Williamston, Michigan'

JOBS = [{
  'id': 1,
  'category': 'Administrative assistant',
  'title': 'Administrative Secretary',
  'location': 'Williamston, Michigan',
  'salary': '$40,000.00'
}, {
  'id': 2,
  'category': 'Information technology',
  'title': 'Data Entry Clerk',
  'location': 'Remotedly'
}, {
  'id': 3,
  'category': 'Accounting',
  'title': 'Accountant',
  'location': 'Williamston, Michigan',
  'salary': '$65,000.00'
}, {
  'id': 4,
  'category': 'Administrative assistant',
  'title': 'Receptionist',
  'location': 'Williamston, Michigan',
  'salary': '$35,000.00'
}, {
  'id': 5,
  'category': 'Healthcare',
  'title': 'Site Inspector',
  'location': 'Williamston, Michigan',
  'salary': '$55,000.00'
}, {
  'id': 6,
  'category': 'Healthcare',
  'title': 'Operator',
  'location': 'Remotedly'
}]


@app.route("/")
def hello_world():
  return render_template('home.html', jobs=JOBS, company_name=COMPANY)


@app.route("/api/jobs")
def job_list():
  return jsonify(JOBS)

@app.route("/jobs-table")
def jobs_table():
  return render_template('jobs.html')













if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)