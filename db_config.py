import os
from dotenv import load_dotenv

load_dotenv() # Ensure environment variables from .env are loaded

def get_db_connection_params():
    """
    Retrieves MariaDB connection parameters from environment variables.
    Returns:
        dict: A dictionary containing host, user, password, and database.
              Returns None for a parameter if its env var is not set.
    """
    params = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME')
    }
    if not all(params.values()):
        # Or raise an error, or handle missing params as appropriate
        print("Warning: Not all database connection parameters are set in .env file.") 
    return params
