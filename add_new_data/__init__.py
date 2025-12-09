import logging
import json
import azure.functions as func
from azure.core.exceptions import ResourceNotFoundError, AzureError
import sys
import os

# Add parent directory to path for shared imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.azure_client import AzureBlobClient
from shared.user_manager import extract_user_id


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Add a new entry to a JSON array in blob storage with user isolation.
    
    Parameters (in JSON body):
    - target_blob_name (required): Name of the file to update (e.g., "tasks.json")
    - new_entry (required): JSON object/data to append to the array
    - user_id (optional): User ID (extracted from header/query/body)
    
    Returns:
    - Success response with entry count
    """
    logging.info('add_new_data: Processing HTTP request with user isolation')
    
    # Parse request body
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON in request body"}),
            status_code=400,
            mimetype="application/json"
        )
    
    # Extract required parameters
    target_blob_name = req_body.get('target_blob_name')
    new_entry = req_body.get('new_entry')
    
    if not target_blob_name or not new_entry:
        return func.HttpResponse(
            json.dumps({"error": "Missing required fields: 'target_blob_name' or 'new_entry'"}),
            status_code=400,
            mimetype="application/json"
        )
    
    # Extract user ID from request
    user_id = extract_user_id(req)
    logging.info(f"add_new_data: user_id={user_id}, file_name={target_blob_name}")
    
    try:
        # Get blob client with user isolation
        blob_client = AzureBlobClient.get_blob_client(target_blob_name, user_id)
        
        # 1. Read existing data or create empty list
        try:
            blob_data = blob_client.download_blob()
            data_str = blob_data.readall().decode('utf-8')
            data = json.loads(data_str)
        except ResourceNotFoundError:
            data = []
        
        # 2. Ensure data is a list
        if not isinstance(data, list):
            data = [data]
        
        # 3. Append new entry
        data.append(new_entry)
        
        # 4. Write updated data back
        upload_data = json.dumps(data, indent=2, ensure_ascii=False)
        blob_client.upload_blob(upload_data.encode('utf-8'), overwrite=True)
        
        response_data = {
            "status": "success",
            "message": f"Entry successfully added to '{target_blob_name}'",
            "entry_count": len(data),
            "user_id": user_id
        }
        
        return func.HttpResponse(
            json.dumps(response_data, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )

    except AzureError as e:
        logging.error(f"Azure error in add_new_data: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Azure storage error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Unexpected error in add_new_data: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )