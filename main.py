from flask import Flask, render_template, jsonify, request, redirect, url_for
from database import Database
from dotenv import load_dotenv
import base64
import os
import sys
import gotrue
from gotrue.errors import AuthApiError
import psycopg2
from psycopg2 import sql
from datetime import datetime


load_dotenv() # Load environment variables from .env

db_url = os.getenv('DATABASE_URL')

app = Flask(__name__)

COMPANY = 'City of Williamston, Michigan'
supabase = Database()


# Function to establish a database connection
def get_db_connection():
    return psycopg2.connect(db_url)


def signout():
  res = supabase.getInstance().supabase_client.auth.sign_out()


def fetch_jobs_from_database():
  """
    Fetch jobs from the database using Supabase.
    """
  response = supabase.getInstance().fetch_from_database("jobs")

  # Format the salary for each job
  for job in response:
    if 'salary' in job and job['salary'] is not None:
      job['salary'] = format_salary(job['salary'])


  # # Sort the jobs by their 'id' in ascending order
  # sorted_jobs = sorted(response.data, key=lambda x: x['id'])
  # return sorted_jobs

  # Reverse the order of jobs
  reversed_jobs = list(reversed(response))

  return reversed_jobs


def fetch_contents_from_database():
  """
    Fetch contents from the database using Supabase.
    """
  response = supabase.getInstance().fetch_from_database("contents")

  # Ensure that response is a list of dictionaries
  if isinstance(response, list):
      # Iterate over each dictionary in the list
      for item in response:
          # Check if 'content' key is present and not None
          if 'content' in item and item['content'] is not None:
              # Update 'content' key with line breaks
              item['content'] = break_line(item['content'])

  # Sort the contents by their 'id' in ascending order
  sorted_contents = sorted(response, key=lambda x: x['id'])

  return sorted_contents


def fetch_job_info(job_id):
  """
    Fetch a job from the database using input job_id
  """
  response = supabase.getInstance().fetch_from_database_by_id("jobs", job_id)

  # Format the salary for the job if it exists
  if response and 'salary' in response and response['salary'] is not None:
    response['salary'] = format_salary(response['salary'])

  if 'responsibilities' in response and response['responsibilities'] is not None:
    response['responsibilities'] = break_line(response['responsibilities'])

  if 'requirements' in response and response['requirements'] is not None:
    response['requirements'] = break_line(response['requirements'])

  if 'benefits' in response and response['benefits'] is not None:
    response['benefits'] = break_line(response['benefits'])

  if 'created_at' in response and response['created_at'] is not None:
    # Parse the string into a datetime object
    # '%Y-%m-%dT%H:%M:%S.%f%z' is the format code matching your date string
    date_obj = datetime.strptime(response['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z')

    # Format the datetime object into a new string format
    # For example, to get 'Month Day, Year - Hour:Minute AM/PM'
    formatted_date = date_obj.strftime('%B %d, %Y - %I:%M %p')
    response['created_at'] = formatted_date

  if 'updated_at' in response and response['updated_at'] is not None:
    date_obj = datetime.strptime(response['updated_at'], '%Y-%m-%dT%H:%M:%S.%f%z')
    formatted_date = date_obj.strftime('%B %d, %Y - %I:%M %p')
    response['updated_at'] = formatted_date

  if 'deadline' in response and response['deadline'] is not None:
    # Parse the string into a datetime object
    # '%Y-%m-%d' is the format code matching your date string (Year-Month-Day)
    date_obj = datetime.strptime(response['deadline'], '%Y-%m-%d')

    # Format the datetime object into a new string format
    # For example, 'Month Day, Year'
    formatted_date = date_obj.strftime('%B %d, %Y')
    response['deadline'] = formatted_date

  return response

def format_salary2(salary):
  try:
    # Convert salary to float and format it without cents
    formatted_salary = f"${float(salary):,.0f}"
    return formatted_salary
  except (ValueError, TypeError):
    # Return the original salary if there's an issue formatting
    return salary

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


def is_signed_in():
  return Database.getInstance().supabase_client.auth.get_user() is not None

def is_admin():
  if not is_signed_in():
    return False

  user = supabase.getInstance().supabase_client.auth.get_user()

  response = Database.getInstance().supabase_client.table('users') \
    .select('admin') \
    .eq("email", user.user.email) \
    .execute()

  return response.data[0]['admin'] if response.data else False

@app.route("/")
@app.route("/home")
def home():
  jobs = fetch_jobs_from_database()
  contents = fetch_contents_from_database()
  signedIn = is_signed_in()
  admin = is_admin()

  # Get the page number from the request
  page = request.args.get('page', 1, type=int)

  # Number of jobs to show per page
  jobs_per_page = 10

  # Calculate the starting and ending indices for the current page
  start_index = (page - 1) * jobs_per_page
  end_index = start_index + jobs_per_page

  # Slice the jobs list to get the jobs for the current page
  jobs_for_page = jobs[start_index:end_index]

  # Calculate the total number of pages
  total_pages = (len(jobs) + jobs_per_page - 1) // jobs_per_page

  return render_template('home.html',
                         jobs=jobs_for_page,
                         total_pages=total_pages,
                         current_page=page,
                         contents=contents,
                         company_name=COMPANY,
                         signedIn=signedIn,
                         admin=admin)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == "GET":
        return render_template("signup.html", signedIn=False)

    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        # Use Database.getInstance() to get the instance and perform user signup
        db_instance = Database.getInstance()
        db_instance.supabase_client.auth.sign_up({
            "email": email,
            "password": password,
        })

        # Insert user data into the 'users' table
        db_instance.insert_to_database('users', {
            "email": email,
            "admin": False
        })
        return redirect(url_for("email_confirm"))

    return redirect("/")


@app.route("/login", methods=['GET', 'POST'])
def login():
  if(request.method == "GET"):
    if(is_signed_in() == True):
      return redirect("/")

    error = None if request.args.get("errorMessage") is None else request.args.get("errorMessage")

    if(error is not None):
      return render_template("login.html", signedIn=False, errorMessage=error, admin=False)

    return render_template("login.html", signedIn=False, errorMessage=None, admin=False)

  email = request.form.get('email')
  password = request.form.get('password')
  data = supabase.getInstance().supabase_client.auth.sign_in_with_password({
    "email": email, 
    "password": password
  })
  return redirect("/")


@app.route("/logout", methods=['POST'])
def logout():
    res = Database.getInstance().supabase_client.auth.sign_out()
    return redirect("/")


@app.route("/email-confirm")
def email_confirm():
  if(is_signed_in() == True):
    return redirect("/")
  return render_template("email-confirm.html", signedIn=False, admin=False)


@app.route("/api/jobs")
def job_list():
  jobs = fetch_jobs_from_database()
  return jsonify(jobs)


@app.route("/job-post-manager")
def job_post_manager():
    if not is_signed_in():
        return redirect("/")

    user = supabase.getInstance().supabase_client.auth.get_user()

    # Fetch user data from the 'users' table using the Database class
    user_data = supabase.getInstance().auth_by_email('users', user.user.email)

    if user_data and user_data.get('admin') is True:
        return render_template('job-post-manager.html', signedIn=True, admin=True)
    else:
        return redirect("/")


@app.route("/job-application-manager")
def job_application_manager():
  if not is_signed_in():
    return redirect("/")

  user = supabase.getInstance().supabase_client.auth.get_user()

  # Fetch user data from the 'users' table using the Database class
  user_data = supabase.getInstance().auth_by_email('users', user.user.email)

  if user_data and user_data.get('admin') is True:
    return render_template('job-application-manager.html', signedIn=True, admin=True)
  else:
    return redirect("/")



@app.route("/application/<int:id>", methods=['GET', 'POST'])
def get_job_info(id):
    job = fetch_job_info(id)

    if job is None:
        # Handle the case when job is None, e.g., show an error message or redirect
        return render_template('404.html'), 404

    if request.method == "POST":
        name = request.form.get("inputName")
        email = request.form.get("inputEmail")
        phone_number = request.form.get("inputPhone")
        linkedin = request.form.get("linkedin")
        education = request.form.get("inputEducation")
        experience = request.form.get("inputWorkExperience")
        resume = request.files.get("resume")
        resume_data = base64.b64encode(resume.read()).decode('utf-8')

        conn = get_db_connection()  
        if conn:
            try:
                cursor = conn.cursor()

                # Define the insert query
                # String formatting and parameterized querying in PostgreSQL
                insert_query = sql.SQL("""
                    INSERT INTO applications (name, email, phone_number, linkedin, education, experience, job_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """)

                cursor.execute(insert_query, (name, email, phone_number, linkedin, education, experience, id))
                conn.commit()
            except psycopg2.Error as e:
                print(f"Error inserting data into the database: {e}")
            finally:
                cursor.close()
                conn.close()

            return redirect(url_for("applied_success"))

    return render_template('application.html', job=job, signedIn=is_signed_in(), admin=is_admin())


@app.route("/applied-success")
def applied_success():
  return render_template('applied-success.html')


@app.errorhandler(gotrue.errors.AuthApiError)
def handleAuthError(e):
  print(e.message, flush=True)
  if(e.message == "Invalid login credentials" or e.message == "Email not confirmed"):
    return redirect(url_for("login", errorMessage=e.message))
  return "Error"

@app.errorhandler(gotrue.errors.AuthInvalidCredentialsError)
def handleCredError(e):
  print(e.message, flush=True)
  return redirect(url_for("login", errorMessage=e.message))

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


# script entry point
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
