import logging
import json
import os
import azure.functions as func
from azure.storage.blob import BlobServiceClient

# Pobieranie zmiennych środowiskowych
CONN_STR = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
CONTAINER_NAME = os.environ.get('AZURE_BLOB_CONTAINER_NAME')

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function (update_data_entry) processed a request.')

    if not CONN_STR or not CONTAINER_NAME:
        return func.HttpResponse(
             json.dumps({"status": "error", "message": "Brak konfiguracji połączenia z Blob Storage."}, indent=2),
             mimetype="application/json",
             status_code=500
        )

    # --- 1. PARSOWANIE DANYCH WEJŚCIOWYCH ---
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(json.dumps({"status": "error", "message": "Nieprawidłowy format JSON."}, indent=2), mimetype="application/json", status_code=400)

    # Argumenty do znalezienia rekordu
    target_blob_name = req_body.get('target_blob_name')
    find_key = req_body.get('find_key')     # np. 'id'
    find_value = req_body.get('find_value') # np. 'T002'

    # Argumenty do aktualizacji rekordu
    update_key = req_body.get('update_key')   # np. 'status'
    update_value = req_body.get('update_value') # np. 'done'

    if not all([target_blob_name, find_key, find_value, update_key, update_value]):
         return func.HttpResponse(json.dumps({"status": "error", "message": "Brak wymaganych argumentów do znalezienia i aktualizacji rekordu."}, indent=2), mimetype="application/json", status_code=400)

    # --- 2. LOGIKA AKTUALIZACJI ---
    try:
        blob_service_client = BlobServiceClient.from_connection_string(CONN_STR)
        blob_client = blob_service_client.get_blob_client(CONTAINER_NAME, target_blob_name)

        # Pobranie aktualnego pliku
        download_stream = blob_client.download_blob()
        data_list = json.loads(download_stream.readall().decode('utf-8'))
        
        entry_updated = False
        
        # Iteracja i aktualizacja
        for item in data_list:
            if str(item.get(find_key)).lower() == str(find_value).lower():
                # Zmiana wartości w znalezionym obiekcie
                item[update_key] = update_value
                entry_updated = True
                logging.info(f"Zaktualizowano rekord '{find_value}': zmieniono '{update_key}' na '{update_value}'.")
                break # Zakładamy, że klucz jest unikalny, przerywamy po znalezieniu

        if not entry_updated:
            return func.HttpResponse(
                json.dumps({"status": "warning", "message": f"Nie znaleziono rekordu o kluczu '{find_key}'='{find_value}'."}, indent=2),
                mimetype="application/json",
                status_code=404
            )

        # Zapisanie zmodyfikowanej listy (nadpisanie)
        modified_data = json.dumps(data_list, indent=2)
        blob_client.upload_blob(modified_data, overwrite=True)

        # --- 3. ZWROT WYNIKU DO AGENTA ---
        message = f"Pomyślnie zaktualizowano rekord {find_key}={find_value} w pliku '{target_blob_name}'. Ustawiono {update_key} na {update_value}."
        return func.HttpResponse(
            json.dumps({"status": "success", "message": message, "updated_key": update_key, "updated_value": update_value}, indent=2),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Global Error in update_data_entry: {e}")
        return func.HttpResponse(
             json.dumps({"status": "server_error", "message": f"Krytyczny błąd: {e}"}, indent=2),
             mimetype="application/json",
             status_code=500
        )