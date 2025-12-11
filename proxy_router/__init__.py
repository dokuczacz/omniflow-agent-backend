import logging
import azure.functions as func
import requests
import os

# Pełne mapowanie akcji do endpointów
# Function codes should be retrieved from environment variables or Azure Key Vault
# See README for deployment instructions
ACTION_MAP = {
    "get_current_time": {
        "method": "GET",
        "url": os.getenv("FUNCTION_URL_BASE", "https://agentbackendservice.azurewebsites.net") + "/api/get_current_time",
        "code": os.getenv("FUNCTION_CODE_GET_TIME", "")
    },
    "add_new_data": {
        "method": "POST",
        "url": os.getenv("FUNCTION_URL_BASE", "https://agentbackendservice.azurewebsites.net") + "/api/add_new_data",
        "code": os.getenv("FUNCTION_CODE_ADD_DATA", "")
    },
    "get_filtered_data": {
        "method": "POST",
        "url": os.getenv("FUNCTION_URL_BASE", "https://agentbackendservice.azurewebsites.net") + "/api/get_filtered_data",
        "code": os.getenv("FUNCTION_CODE_GET_DATA", "")
    },
    "manage_files": {
        "method": "POST",
        "url": os.getenv("FUNCTION_URL_BASE", "https://agentbackendservice.azurewebsites.net") + "/api/manage_files",
        "code": os.getenv("FUNCTION_CODE_MANAGE_FILES", "")
    },
    "update_data_entry": {
        "method": "POST",
        "url": os.getenv("FUNCTION_URL_BASE", "https://agentbackendservice.azurewebsites.net") + "/api/update_data_entry",
        "code": os.getenv("FUNCTION_CODE_UPDATE_DATA", "")
    },
    "remove_data_entry": {
        "method": "POST",
        "url": os.getenv("FUNCTION_URL_BASE", "https://agentbackendservice.azurewebsites.net") + "/api/remove_data_entry",
        "code": os.getenv("FUNCTION_CODE_REMOVE_DATA", "")
    },
    "upload_data_or_file": {
        "method": "POST",
        "url": os.getenv("FUNCTION_URL_BASE", "https://agentbackendservice.azurewebsites.net") + "/api/upload_data_or_file",
        "code": os.getenv("FUNCTION_CODE_UPLOAD", "")
    },
    "list_blobs": {
        "method": "GET",
        "url": os.getenv("FUNCTION_URL_BASE", "https://agentbackendservice.azurewebsites.net") + "/api/list_blobs",
        "code": os.getenv("FUNCTION_CODE_LIST_BLOBS", "")
    },
    "read_blob_file": {
        "method": "GET",
        "url": os.getenv("FUNCTION_URL_BASE", "https://agentbackendservice.azurewebsites.net") + "/api/read_blob_file",
        "code": os.getenv("FUNCTION_CODE_READ_BLOB", "")
    },
    "save_interaction": {
        "method": "POST",
        "url": os.getenv("FUNCTION_URL_BASE", "https://agentbackendservice.azurewebsites.net") + "/api/save_interaction",
        "code": os.getenv("FUNCTION_CODE_SAVE_INTERACTION", "")
    },
    "get_interaction_history": {
        "method": "GET",
        "url": os.getenv("FUNCTION_URL_BASE", "https://agentbackendservice.azurewebsites.net") + "/api/get_interaction_history",
        "code": os.getenv("FUNCTION_CODE_GET_HISTORY", "")
    }
}

# Parameter validation: required keys for each action
ACTION_SCHEMA = {
    "read_blob_file": ["file_name"],
    "get_filtered_data": ["target_blob_name"],
    "remove_data_entry": ["target_blob_name", "key_to_find", "value_to_find"],
    "update_data_entry": ["target_blob_name", "find_key", "find_value", "update_key", "update_value"],
    "upload_data_or_file": ["target_blob_name", "file_content"],
    "add_new_data": ["target_blob_name", "new_entry"],
    "manage_files": ["operation"],
    "save_interaction": ["user_message", "assistant_response"],
    # Other actions don't require parameters
}

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("proxy_router triggered")

    try:
        data = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON payload", status_code=400)

    action = data.get("action")
    params = data.get("params", {})

    if not action or action not in ACTION_MAP:
        return func.HttpResponse("Invalid or missing 'action'", status_code=400)

    # Walidacja parametrów
    required_keys = ACTION_SCHEMA.get(action, [])
    missing = [key for key in required_keys if key not in params]
    if missing:
        return func.HttpResponse(
            f"Missing required parameters: {', '.join(missing)}",
            status_code=400
        )

    endpoint = ACTION_MAP[action]
    method = endpoint["method"]
    url = endpoint["url"]
    code = endpoint["code"]

    try:
        if method == "GET":
            query_params = params.copy()
            query_params["code"] = code
            res = requests.get(url, params=query_params)
        elif method == "POST":
            res = requests.post(f"{url}?code={code}", json=params)
        else:
            return func.HttpResponse("Unsupported method", status_code=400)

        return func.HttpResponse(
            res.text,
            status_code=res.status_code,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error calling backend: {str(e)}")
        return func.HttpResponse("Internal server error", status_code=500)
