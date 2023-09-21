import psycopg2

# Replace these with your actual database credentials
db_host = 'db.xsqouwxwkxlryycnvoac.supabase.co'
db_port = 5432
db_name = 'postgres'
db_user = 'postgres'
db_password = 'lWAlQIjqUfLL1osB'

try:
    # Establish a connection to the PostgreSQL database
    connection = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password
    )

    # Create a cursor object
    cursor = connection.cursor()

    # Execute a simple query to test the connection
    cursor.execute("SELECT 1")

    # Fetch the result
    result = cursor.fetchone()
    print("Database connection successful. Result:", result[0])

    # Close the cursor and the connection
    cursor.close()
    connection.close()

except Exception as e:
    print("Database connection failed. Error:", str(e))
