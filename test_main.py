import pytest
from unittest.mock import MagicMock
from main import home, fetch_jobs_from_database, fetch_contents_from_database, fetch_job_info, app
from dotenv import load_dotenv
from supabase import create_client
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify


supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

job_table_name = 'jobs'
content_table_name = 'contents'

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_job_data():
    # Sample jobs data for testing
    return [
        {'id': 9, 'title': 'Web Developer', 'location': 'Remote'},
        {'id': 12, 'title': 'Data Entry Clerk', 'location': 'Williamston, Michigan'}
    ]

@pytest.fixture
def sample_content_data():
    # Sample content data for testing
    return [
        {'id': 1, 'content': 'Test case',
         'description': 'About City', 
         'intro_title': 'test', 
         'content_title': 'test'}
    ]

def test_fetch_contents_from_database(sample_content_data):
  # Call the function
  result = fetch_contents_from_database()

  # Ensure the expected item has the correct structure
  expected_item = sample_content_data[0]

  # Check if the expected item is a subset of any item in the result list
  assert any(expected_item.items() <= item.items() for item in result), \
      f"Expected item {expected_item} not found in result: {result}"



def test_fetch_jobs_from_database(sample_job_data):
  # Call the function
  result = fetch_jobs_from_database()

  # Convert data types in the result list to match sample_data
  converted_result = [
    {
        "id": item["id"],
        "title": item["title"],
        "location": item["location"]
    }
    for item in result
  ]

    # Assert the result based on the mock response
  for expected_item in sample_job_data:
    assert expected_item in converted_result

def test_fetch_job_info(sample_job_data):
  # Call the function
  result = fetch_job_info(12)
  expected_result = sample_job_data[1]
  assert all(item in result.items() for item in expected_result.items())

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    # Add more assertions based on your expected response

def test_api_jobs(client):
    response = client.get('/api/jobs')
    assert response.status_code == 200
    # Add more assertions based on your expected response

def test_job_info_page(client):
    response = client.get('/application/1')  # replace 1 with a valid job id
    assert response.status_code == 200
    # Add more assertions based on your expected response