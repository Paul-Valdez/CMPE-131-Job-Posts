from flask import Flask, render_template, jsonify, request, redirect, url_for
from dotenv import load_dotenv
import base64

load_dotenv()
import os
import sys
from supabase import create_client
import gotrue

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

def signout():
  res = supabase.auth.sign_out()

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


def fetch_contents_from_database():
  """
    Fetch contents from the database using Supabase.
    """
  response = supabase.table("contents").select("id, description, content",
                                               count='exact').execute()

  if hasattr(response, 'data') and 'error' in response.data:
    print("Error fetching data:", response.data['error'])
    return []

  # Sort the contents by their 'id' in ascending order
  sorted_contents = sorted(response.data, key=lambda x: x['id'])

  return sorted_contents


def fetch_job_info(job_id):
  """
    Fetch a job from the database using input job_id
  """
  response = supabase.table("jobs").select(
    "id, title, location, responsibilities, benefits, category, salary, requirements"
  ).eq("id", job_id).execute()
  

  if hasattr(response, 'data') and 'error' in response.data:
    print("Error fetching data:", response.data['error'])
    return None

  job = response.data[0] if response.data else None

  # Format the salary for the job if it exists
  if job and 'salary' in job and job['salary'] is not None:
    job['salary'] = format_salary(job['salary'])

  if 'responsibilities' in job and job['responsibilities'] is not None:
    job['responsibilities'] = break_line(job['responsibilities'])
  
  if 'requirements' in job and job['requirements'] is not None:
    job['requirements'] = break_line(job['requirements'])

  if 'benefits' in job and job['benefits'] is not None:
    job['benefits'] = break_line(job['benefits'])

  return job


def format_salary(salary):
  try:
    # Convert salary to float and format it without cents
    formatted_salary = f"${float(salary):,.0f}"
    return formatted_salary
  except (ValueError, TypeError):
    # Return the original salary if there's an issue formatting
    return salary

def break_line(s):
  try:
    # Replace text in responsibilities
    new_string = s.replace('.', '. <br>')
    return new_string
  except (ValueError, TypeError):
    # Return the original string if there's an issue formatting
    return s

def isSignedIn():
  return supabase.auth.get_user() != None

@app.route("/")
@app.route("/home")
def hello_world():
  jobs = fetch_jobs_from_database()
  contents = fetch_contents_from_database()
  signedIn = isSignedIn()
  
  return render_template('home.html',
                         jobs=jobs,
                         contents=contents,
                         company_name=COMPANY,
                         signedIn=signedIn)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
  if(request.method == "GET"):
    return render_template("signup.html", signedIn=False)
  if(request.method == "POST"):
    email = request.form['email']
    password = request.form['password']
    res = supabase.auth.sign_up({
      "email": email,
      "password": password,
    })
    supabase.table('users').insert({
      "email": email,
      "admin": False
    }).execute()
    return redirect(url_for("email_confirm"))
  return redirect("/")
    
@app.route("/login", methods=['GET', 'POST'])
def login():
  if(request.method == "GET"):
    if(isSignedIn() == True):
      return redirect("/")
    invalidCred = False if request.args.get("invalidCredentials") is None else request.args.get("invalidCredentials")
    if(invalidCred == "True"):
      return render_template("login.html", signedIn=False, invalidCredentials=True)
    return render_template("login.html", signedIn=False, invalidCredentials=False)
  email = request.form['email']
  password = request.form['password']
  data = supabase.auth.sign_in_with_password({
    "email": email, 
    "password": password
  })
  return redirect("/")

@app.route("/logout", methods=['POST'])
def logout():
  res = supabase.auth.sign_out()
  return redirect("/")

@app.route("/email-confirm")
def email_confirm():
  signedIn = isSignedIn()
  return render_template("email-confirm.html", signedIn=signedIn)

@app.route("/api/jobs")
def job_list():
  jobs = fetch_jobs_from_database()
  return jsonify(jobs)

@app.route("/job-post-manager")
def jobs_table():
  if(isSignedIn() == False):
    return redirect("/")
  elif(isSignedIn() == True):
    user = supabase.auth.get_user()
    response = supabase.table('users').select('admin').eq("email", user.user.email).execute()
    if(response.data[0]['admin'] != True):
      return redirect("/")
  return render_template('job-post-manager.html')


@app.route("/application/<int:id>", methods=['GET', 'POST'])
def get_job_info(id):
  job = fetch_job_info(id)
  if request.method == "POST":
    name = request.form.get("inputName")
    email = request.form.get("inputEmail")
    linkedin = request.form.get("linkedin")
    education = request.form.get("inputEducation")
    experience = request.form.get("inputWorkExperience")
    resume = request.files.get("resume")
    resume_data = base64.b64encode(resume.read()).decode('utf-8')

    supabase.table('applicants').insert({
      "name": name,
      "email": email,
      "linkedin": linkedin,
      "education": education,
      "experience": experience,
      "job_id": id,
      "resume": resume_data
    }).execute()
    return redirect(url_for("applied_success"))
  if(isSignedIn() == False):
    return redirect("/")
  return render_template('application.html', job=job)


@app.route("/applied-success")
def applied_success():
  return render_template('applied-success.html')

@app.errorhandler(gotrue.errors.AuthApiError)
def handleError(e):
  print(e.message, flush=True)
  if(e.message == "Invalid login credentials"):
    return redirect(url_for("login", invalidCredentials=True))
  return "Error"

# script entry point
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)

