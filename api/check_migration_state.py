#!/usr/bin/env python
"""
This script checks the current migration state and runs diagnostics.
It helps identify problems with database connections and Alembic configuration.
"""
import os
import sys
from sqlalchemy import create_engine, text
from getpass import getpass
import traceback

def check_database_connection(connection_string):
    """Test the connection to the database"""
    print(f"Testing connection to database...")
    try:
        # Create an engine and connect
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            # Try a simple query
            result = conn.execute(text("SELECT version()"))
            for row in result:
                print(f"PostgreSQL version: {row[0]}")
        print("Database connection successful!")
        return True
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        traceback.print_exc()
        return False

def check_alembic_table(connection_string):
    """Check if the alembic_version table exists"""
    print(f"Checking for alembic_version table...")
    try:
        # Create an engine and connect
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            # Try to query the alembic_version table
            result = conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')"
            ))
            exists = result.scalar()
            if exists:
                # Get the current version
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                version = result.scalar()
                print(f"Alembic version table exists. Current version: {version}")
            else:
                print("Alembic version table does not exist. No migrations have been run yet.")
            return exists
    except Exception as e:
        print(f"Error checking alembic table: {str(e)}")
        traceback.print_exc()
        return False

def check_transcripts_table(connection_string):
    """Check if the transcripts table exists and its structure"""
    print(f"Checking transcripts table structure...")
    try:
        # Create an engine and connect
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            # Check if the table exists
            result = conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'transcripts')"
            ))
            exists = result.scalar()
            if exists:
                # Get the columns of the table
                result = conn.execute(text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'transcripts'"
                ))
                columns = [row[0] for row in result]
                print(f"Transcripts table exists with columns: {', '.join(columns)}")
                
                # Check if the "metadata" column exists
                if "metadata" in columns:
                    print("The 'metadata' column exists and needs to be renamed.")
                elif "transcript_metadata" in columns:
                    print("The 'transcript_metadata' column already exists. Migration may have already been applied.")
                else:
                    print("Neither 'metadata' nor 'transcript_metadata' columns found in the transcripts table.")
            else:
                print("Transcripts table does not exist.")
            return exists
    except Exception as e:
        print(f"Error checking transcripts table: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Get connection string
    connection_string = os.environ.get("DATABASE_URL")
    if not connection_string:
        # Prompt for Neon credentials
        username = input("Enter Neon database username [neondb_owner]: ") or "neondb_owner"
        password = getpass("Enter Neon database password: ")
        host = input("Enter Neon host [ep-lingering-cloud-acvjfrnh-pooler.sa-east-1.aws.neon.tech]: ") or "ep-lingering-cloud-acvjfrnh-pooler.sa-east-1.aws.neon.tech"
        database = input("Enter database name [summary_tube_db]: ") or "summary_tube_db"
        
        # Form the connection string
        connection_string = f"postgresql://{username}:{password}@{host}/{database}?sslmode=require"
    
    # Run the checks
    print("\n=== Database Connection Check ===")
    if check_database_connection(connection_string):
        print("\n=== Alembic Migration State ===")
        check_alembic_table(connection_string)
        
        print("\n=== Transcripts Table Check ===")
        check_transcripts_table(connection_string)
    
    print("\nDiagnostics complete.")
