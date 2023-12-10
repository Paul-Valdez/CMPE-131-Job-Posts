from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Database:
  __instance = None

  def __init__(self):
      if Database.__instance is not None:
          raise Exception("This class is a singleton. Use getInstance() to get the instance.")

      supabase_url = os.getenv('SUPABASE_URL')
      supabase_key = os.getenv('SUPABASE_KEY')

      self.supabase_client = create_client(supabase_url, supabase_key)

  @classmethod
  def getInstance(cls):
      if cls.__instance is None:
          cls.__instance = cls()
      return cls.__instance

  @staticmethod
  def fetch_from_database(table_name):
      response = Database.getInstance().supabase_client.table(table_name).select("*").execute()

      if hasattr(response, 'data') and 'error' in response.data:
          print("Error fetching data:", response.data['error'])
          return []

      return response.data

  @staticmethod
  def fetch_from_database_by_id(table_name, id):
      response = Database.getInstance().supabase_client.table(table_name).select("*").eq("id", id).execute()

      if hasattr(response, 'data') and 'error' in response.data:
          print("Error fetching data:", response.data['error'])
          return []

      return response.data[0] if response.data else None

  @staticmethod
  def auth_by_email(table_name, email):
    response = Database.getInstance().supabase_client.table(table_name).select("*").eq("email", email).execute()

    if hasattr(response, 'data') and 'error' in response.data:
      print("Error fetching data:", response.data['error'])
      return []

    return response.data[0] if response.data else None


  def insert_to_database(self, table_name, data):
    try:
        # Use supabase_client to insert data into the specified table
        response = self.supabase_client.table(table_name).insert(data).execute()
        if response.get('error') is not None:
            # Handle insertion error, e.g., log the error or raise an exception
            raise Exception(f"Error inserting data into {table_name}: {response['error']['message']}")
        return True  # Insertion successful
    except Exception as e:
        # Handle other exceptions, e.g., log the error or raise an exception
        raise Exception(f"Error inserting data into {table_name}: {str(e)}")