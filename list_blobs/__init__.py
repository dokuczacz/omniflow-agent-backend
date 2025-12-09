import json
import logging
import azure.functions as func
from azure.core.exceptions import AzureError
import sys
import os

# Add parent directory to path for shared imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.azure_client import AzureBlobClient
from shared.user_manager import extract_user_id


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    List all blobs for the authenticated user.
    
    Parameters:
    - prefix (optional): Filter blobs by name prefix (e.g., "tasks" to find "tasks.json", "tasks_backup.json")
    - user_id (optional): User ID (from header X-User-Id, query param, or body)
    
    Returns:
    - JSON array of blob names
    """
    # Extract user ID and optional prefix
    user_id = extract_user_id(req)
    prefix = req.params.get("prefix")
    
    logging.info(f"list_blobs: user_id={user_id}, prefix={prefix}")
    
    try:
        # Get list of blobs for this user
        blobs = AzureBlobClient.list_user_blobs(user_id, prefix)
        
        response = {
            "user_id": user_id,
            "blobs": blobs,
            "count": len(blobs)
        }
        
        return func.HttpResponse(
            json.dumps(response),
            mimetype="application/json",
            status_code=200
        )

    except AzureError as e:
        logging.error(f"Azure error listing blobs for user {user_id}: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Error listing blobs: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Unexpected error in list_blobs: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Unexpected error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
