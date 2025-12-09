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
    Get and optionally filter data from a JSON file with user isolation.
    
    Parameters (in JSON body):
    - target_blob_name (required): Name of the file to read (e.g., "tasks.json")
    - key (optional): Field name to filter by (e.g., "status")
    - value (optional): Value to match (e.g., "open")
    - user_id (optional): User ID (extracted from header/query/body)
    
    Returns:
    - JSON data (filtered if key/value provided, otherwise full data)
    """
    logging.info('get_filtered_data: Processing HTTP request with user isolation')
    
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON in request body"}),
            status_code=400,
            mimetype="application/json"
        )
    
    # Extract parameters
    target_blob_name = req_body.get('target_blob_name')
    key = req_body.get('key')
    value = req_body.get('value')
    
    if not target_blob_name:
        return func.HttpResponse(
            json.dumps({"error": "Missing required field 'target_blob_name'"}),
            status_code=400,
            mimetype="application/json"
        )
    
    # Extract user ID from request
    user_id = extract_user_id(req)
    logging.info(f"get_filtered_data: user_id={user_id}, file_name={target_blob_name}, filter={key}={value if key else 'none'}")
    
    try:
        # Get blob client with user isolation
        blob_client = AzureBlobClient.get_blob_client(target_blob_name, user_id)
        
        # Read blob data
        blob_data = blob_client.download_blob()
        data_str = blob_data.readall().decode('utf-8')
        data = json.loads(data_str)
        
        # Apply filter if provided
        if key and value:
            filtered_data = [entry for entry in data if str(entry.get(key)) == str(value)]
            
            response = {
                "status": "success",
                "user_id": user_id,
                "file": target_blob_name,
                "filter": {"key": key, "value": value},
                "data": filtered_data,
                "count": len(filtered_data),
                "total": len(data)
            }
        else:
            response = {
                "status": "success",
                "user_id": user_id,
                "file": target_blob_name,
                "filter": None,
                "data": data,
                "count": len(data)
            }
        
        return func.HttpResponse(
            json.dumps(response, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )

    except ResourceNotFoundError:
        logging.warning(f"File not found: {target_blob_name} for user {user_id}")
        return func.HttpResponse(
            json.dumps({"error": f"File '{target_blob_name}' not found for user {user_id}"}),
            status_code=404,
            mimetype="application/json"
        )
    except json.JSONDecodeError as e:
        logging.error(f"JSON parsing error in {target_blob_name}: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Invalid JSON format in file: {str(e)}"}),
            status_code=400,
            mimetype="application/json"
        )
    except AzureError as e:
        logging.error(f"Azure error in get_filtered_data: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Azure storage error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Unexpected error in get_filtered_data: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )