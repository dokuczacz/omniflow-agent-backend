import logging
import azure.functions as func
import requests

# Pełne mapowanie akcji do endpointów
ACTION_MAP = {
    "get_current_time": {
        "method": "GET",
        "url": "https://agentbackendservice-dfcpcudzeah4b6ae.northeurope-01.azurewebsites.net/api/get_current_time",
        "code": "3YZLIdIa31Cpjmfy658npf5zjvverr9LDf33xRRV-pZwAzFu01IeHA=="
    },
    "add_new_data": {
        "method": "POST",
        "url": "https://agentbackendservice-dfcpcudzeah4b6ae.northeurope-01.azurewebsites.net/api/add_new_data",
        "code": "9sNbFWhDYoYlc3F5anxyr5aPEp_YHRKhlyOqvBAI1fd9AzFu0PYBmw=="
    },
    "get_filtered_data": {
        "method": "POST",
        "url": "https://agentbackendservice-dfcpcudzeah4b6ae.northeurope-01.azurewebsites.net/api/get_filtered_data",
        "code": "WJXxPhTUVl5VKucG4yDmcYk8a8Yx8J6A__EgD2d28AXPAzFuXjSo1Q=="
    },
    "manage_files": {
        "method": "POST",
        "url": "https://agentbackendservice-dfcpcudzeah4b6ae.northeurope-01.azurewebsites.net/api/manage_files",
        "code": "kIvzmKpf6YrSHDV7cfupRki22AD1VZKxMbx6ac1VGFl0AzFu_uyl3A=="
    },
    "update_data_entry": {
        "method": "POST",
        "url": "https://agentbackendservice-dfcpcudzeah4b6ae.northeurope-01.azurewebsites.net/api/update_data_entry",
        "code": "YMHxj_ec7Si2RFtBGnFQisfvxVVdxU9llvCOJ35R4FWaAzFu6s10LQ=="
    },
    "remove_data_entry": {
        "method": "POST",
        "url": "https://agentbackendservice-dfcpcudzeah4b6ae.northeurope-01.azurewebsites.net/api/remove_data_entry",
        "code": "1VTD_tAtmSSyioE-MEgS27GjClZYBcx8L5WWpS6cSKkuAzFuOHrlew=="
    },
    "upload_data_or_file": {
        "method": "POST",
        "url": "https://agentbackendservice-dfcpcudzeah4b6ae.northeurope-01.azurewebsites.net/api/upload_data_or_file",
        "code": "meLNxvlt2GKcHAL7030oGZkAu4LqoaYZ9pkRUIWWbP1bAzFuCOskXQ=="
    },
    "list_blobs": {
        "method": "GET",
        "url": "https://agentbackendservice-dfcpcudzeah4b6ae.northeurope-01.azurewebsites.net/api/list_blobs",
        "code": "6Y8LeWpCx0gvEx36xOd7SD2uhgO0itPzwSUEUBERN_GRAzFuj16kMQ=="
    },
    "read_blob_file": {
        "method": "GET",
        "url": "https://agentbackendservice-dfcpcudzeah4b6ae.northeurope-01.azurewebsites.net/api/read_blob_file",
        "code": "F2X-DkQpiMFd3KQEqokei8phObtMVEDR7EvvDniY5bqKAzFuG9OSqQ=="
    }
}

# Walidacja parametrów: wymagane klucze dla każdej akcji
ACTION_SCHEMA = {
    "read_blob_file": ["file_name"],
    "get_filtered_data": ["target_blob_name"],
    "remove_data_entry": ["target_blob_name", "key_to_find", "value_to_find"],
    "update_data_entry": ["target_blob_name", "find_key", "find_value", "update_key", "update_value"],
    "upload_data_or_file": ["target_blob_name", "file_content"],
    "add_new_data": ["target_blob_name", "new_entry"],
    "manage_files": ["operation"],
    # Pozostałe nie wymagają parametrów
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
