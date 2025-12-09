import logging
import json
import azure.functions as func
from azure.core.exceptions import ResourceNotFoundError, AzureError
import sys
import os

# Add parent directory to path for shared imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.azure_client import AzureBlobClient, AzureBlobError
from shared.user_manager import extract_user_id, UserValidator


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Read blob file with user isolation.
    
    Parameters:
    - file_name (required): Name of the file to read (e.g., "tasks.json")
    - user_id (optional): User ID (from header X-User-Id, query param, or body)
    
    Returns:
    - JSON file contents
    """
    file_name = req.params.get("file_name")
    if not file_name:
        return func.HttpResponse(
            json.dumps({"error": "Missing 'file_name' parameter"}),
            status_code=400,
            mimetype="application/json"
        )
    
    # Extract user ID from request
    user_id = extract_user_id(req)
    logging.info(f"read_blob_file: user_id={user_id}, file_name={file_name}")
    
    try:
        # Get blob client with user isolation
        blob_client = AzureBlobClient.get_blob_client(file_name, user_id)
        
        # Download and return blob data
        blob_data = blob_client.download_blob().readall()
        return func.HttpResponse(blob_data, mimetype="application/json")

    except ResourceNotFoundError:
        logging.warning(f"File not found: {file_name} for user {user_id}")
        return func.HttpResponse(
            json.dumps({"error": f"File '{file_name}' not found"}),
            status_code=404,
            mimetype="application/json"
        )
    except AzureError as e:
        logging.error(f"Azure error reading {file_name}: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Error reading file: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Unexpected error in read_blob_file: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Unexpected error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
