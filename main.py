from flask import Flask, render_template, jsonify

app = Flask(__name__)

COMPANY = 'City of Williamston, Michigan'

JOBS = [
  {
    'id': 1,
    'category': 'Administrative assistant',
    'title': 'Administrative Secretary',
    'location': 'Williamston, Michigan',
    'salary': '$40,000.00'
  },
  {
    'id': 2,
    'category': 'Information technology',
    'title': 'Data Entry Clerk',
    'location': 'Remotedly'
  },
  {
    'id': 3,
    'category': 'Accounting',
    'title': 'Accountant',
    'location': 'Williamston, Michigan',
    'salary': '$65,000.00'
  },
  {
    'id': 4,
    'category': 'Administrative assistant',
    'title': 'Receptionist',
    'location': 'Williamston, Michigan',
    'salary': '$35,000.00'
  },
  {
    'id': 5,
    'category': 'Healthcare',
    'title': 'Site Inspector',
    'location': 'Williamston, Michigan',
    'salary': '$55,000.00'
  },
  {
    'id': 4,
    'category': 'Healthcare',
    'title': 'Operator',
    'location': 'Remotedly'
  }
]

@app.route("/")
def hello_world():
  return render_template('home.html', jobs = JOBS, company_name = COMPANY)

@app.route("/api/jobs")
def job_list():
  return jsonify(JOBS)

if __name__ == "__main__":
  app.run(host = '0.0.0.0', debug = True)