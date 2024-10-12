import requests
import os
import json
from app.models import SplunkConfig, SplunkAnalysis
from datetime import datetime
from app import db
from flask import render_template, flash, redirect, url_for
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Text, DateTime
from sqlalchemy.exc import OperationalError


class SplunkUtils:
    def __init__(self):
        """
        Initialize the SplunkUtils class by loading the Splunk config from the database.
        """
        self.config = self.load_splunk_config()

    def load_splunk_config(self):
        """
        Load the Splunk configuration from the database.
        - Returns: A dictionary with the Splunk connection details (server_url, auth_token).
        """
        config = SplunkConfig.query.first()
        if not config:
            raise ValueError("Splunk configuration not found in the database.")
        return {
            'server_url': config.server_url,
            'auth_token': config.auth_token
        }

    def query_splunk(self, search_query, earliest="-24h", latest="now"):
        """
        Query the Splunk instance using the REST API.
        - search_query: The search query string.
        - earliest: The earliest time for the search (default: -24 hours).
        - latest: The latest time for the search (default: now).
        - Returns: The search results in JSON format.
        """
        try:
            search_url = f"{self.config['server_url']}/services/search/jobs"
            headers = {
                'Authorization': f"Bearer {self.config['auth_token']}",
                'Content-Type': 'application/json'
            }
            payload = {
                'search': f"search {search_query}",
                'earliest_time': earliest,
                'latest_time': latest,
                'output_mode': 'json'
            }
            response = requests.post(search_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            
            search_results = response.json()
            return search_results

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to query Splunk: {e}")

    def analyze_logs(self, search_query, earliest="-24h", latest="now"):
        """
        Analyze the Splunk logs and categorize them based on log levels (errors, warnings, info).
        - search_query: The search query string (e.g., "error OR warn OR info").
        - earliest: The earliest time for the search (default: -24 hours).
        - latest: The latest time for the search (default: now).
        - Returns: A dictionary summarizing log levels.
        """
        logs = self.query_splunk(search_query, earliest, latest)

        summary = {
            'errors': [],
            'warnings': [],
            'info': []
        }

        # Extract log messages based on severity
        for entry in logs['results']:
            message = entry.get('_raw', '')
            if "error" in message.lower():
                summary['errors'].append(message)
            elif "warn" in message.lower():
                summary['warnings'].append(message)
            else:
                summary['info'].append(message)

        return summary

    def check_db_connection(self):
        """
        Check if there is an active connection to the database.
        - Returns: True if the connection is active, False otherwise.
        """
        try:
            db.session.execute('SELECT 1')
            return True
        except OperationalError:
            return False

    def create_db(self):
        """
        Automatically create the database and table schema if needed.
        """
        try:
            engine = create_engine('sqlite:///splunk_analysis.db')  # Replace with your DB connection string
            meta = MetaData()

            # Define the SplunkAnalysis table
            splunk_analysis = Table(
                'splunk_analysis', meta,
                Column('id', Integer, primary_key=True),
                Column('created_at', DateTime, default=datetime.utcnow),
                Column('error_logs', Text),
                Column('warning_logs', Text),
                Column('info_logs', Text)
            )
                
            meta.create_all(engine)
            print("Database and table created successfully.")

        except Exception as e:
            raise Exception(f"Failed to create the database: {e}")

    def save_analysis_to_db(self, analysis_data):
        """
        Save the log analysis data into a local database for historical tracking.
        - analysis_data: A dictionary containing errors, warnings, and info logs.
        """
        try:
            # Check if a database connection is active
            if not self.check_db_connection():
                flash("No active database connection found. Please set up a database.", "danger")
                return redirect(url_for('main.setup_database'))

            # Save the analysis data to the database
            error_logs = "\n".join(analysis_data['errors'])
            warning_logs = "\n".join(analysis_data['warnings'])
            info_logs = "\n".join(analysis_data['info'])

            analysis = SplunkAnalysis(
                created_at=datetime.utcnow(),
                error_logs=error_logs,
                warning_logs=warning_logs,
                info_logs=info_logs
            )
            db.session.add(analysis)
            db.session.commit()

            flash("Analysis data saved successfully.", "success")
        except Exception as e:
            raise Exception(f"Failed to save analysis data to the database: {e}")

    def list_splunk_jobs(self):
        """
        List all running Splunk jobs using the REST API.
        - Returns: A list of running jobs.
        """
        try:
            jobs_url = f"{self.config['server_url']}/services/search/jobs"
            headers = {
                'Authorization': f"Bearer {self.config['auth_token']}",
                'Content-Type': 'application/json'
            }
            response = requests.get(jobs_url, headers=headers)
            response.raise_for_status()

            jobs = response.json()
            return jobs['entry']

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to list Splunk jobs: {e}")

    def extract_warnings_and_errors(self, earliest="-24h", latest="now"):
        """
        Extract warnings and errors from Splunk logs for a given time range.
        - earliest: The earliest time for the search (default: -24 hours).
        - latest: The latest time for the search (default: now).
        - Returns: A summary of warnings and errors.
        """
        search_query = "error OR warn"
        analysis = self.analyze_logs(search_query, earliest, latest)

        return {
            'errors': analysis['errors'],
            'warnings': analysis['warnings']
        }

    def fetch_splunk_logs(self, earliest="-24h", latest="now"):
        """
        Fetch all logs from Splunk within a given time range.
        - earliest: The earliest time for the search (default: -24 hours).
        - latest: The latest time for the search (default: now).
        - Returns: All log entries.
        """
        search_query = "*"
        logs = self.query_splunk(search_query, earliest, latest)
        return logs['results']
