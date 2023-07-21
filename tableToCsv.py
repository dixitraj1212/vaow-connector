import csv
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
# PostgreSQL connection details


# Database Configuration
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_table = os.getenv('DB_TABLE')


# Establish a connection to the PostgreSQL database
connection = psycopg2.connect(user=db_user,
                              password=db_password,
                              host=db_host,
                              port=db_port,
                              database=db_name)
# Create a cursor object to interact with the database
cursor = connection.cursor()

# Retrieve column names from the table
cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{db_table}'")
column_names = [row[0] for row in cursor.fetchall()]

# Retrieve data from the table
cursor.execute(f"SELECT * FROM {db_table}")
data = cursor.fetchall()

# Close the cursor and database connection
cursor.close()
connection.close()

# Write data to a CSV file
csv_file = "data.csv"

with open(csv_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(column_names)  # Write column names as the first row
    writer.writerows(data)  # Write data rows

print(f"Data successfully exported to {csv_file}.")
