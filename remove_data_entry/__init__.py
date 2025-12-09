import logging
import json
import azure.functions as func
import os
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('remove_data_entry: Przetwarzanie żądania HTTP do usunięcia pojedynczego wpisu.')
    
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Proszę przesłać poprawny JSON w ciele żądania.", status_code=400)

    target_blob_name = req_body.get('target_blob_name')
    # Key i Value identyfikują wpis do usunięcia (np. key='id', value='T008')
    key_to_find = req_body.get('key_to_find')
    value_to_find = req_body.get('value_to_find')

    if not all([target_blob_name, key_to_find, value_to_find]):
        return func.HttpResponse(
             "Brak wymaganych pól: 'target_blob_name', 'key_to_find' lub 'value_to_find'.",
             status_code=400
        )

    try:
        connect_str = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
        container_name = os.environ["AZURE_BLOB_CONTAINER_NAME"]
        
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(target_blob_name)
        
        # 1. Odczyt istniejących danych
        try:
            blob_data = blob_client.download_blob()
            data_str = blob_data.readall().decode('utf-8')
            data_list = json.loads(data_str)
        except ResourceNotFoundError:
            return func.HttpResponse(
                json.dumps({"status": "error", "message": f"Plik '{target_blob_name}' nie istnieje."}),
                mimetype="application/json",
                status_code=404
            )
        
        if not isinstance(data_list, list):
            return func.HttpResponse(
                 json.dumps({"status": "error", "message": "Plik docelowy nie jest listą, operacja DELETE niemożliwa."}),
                 mimetype="application/json",
                 status_code=500
            )

        # 2. Usuwanie wpisu
        
        # Nowa lista zawierająca tylko te wpisy, które NIE pasują do kryterium
        initial_count = len(data_list)
        
        # Używamy list comprehension do utworzenia nowej listy bez pasujących elementów
        modified_data_list = [
            entry for entry in data_list 
            if str(entry.get(key_to_find)) != str(value_to_find)
        ]
        
        deleted_count = initial_count - len(modified_data_list)

        if deleted_count == 0:
            return func.HttpResponse(
                json.dumps({"status": "not_found", "message": f"Nie znaleziono wpisu spełniającego kryterium {key_to_find}={value_to_find} do usunięcia."}),
                mimetype="application/json",
                status_code=404
            )

        # 3. Zapis zmodyfikowanej listy (nadpisanie)
        upload_data = json.dumps(modified_data_list, indent=2, ensure_ascii=False)
        blob_client.upload_blob(upload_data.encode('utf-8'), overwrite=True)

        response_data = {
            "status": "success",
            "message": f"Pomyślnie usunięto {deleted_count} wpisów spełniających kryterium {key_to_find}={value_to_find}."
        }
        
        return func.HttpResponse(
            json.dumps(response_data, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Krytyczny błąd w remove_data_entry: {e}")
        return func.HttpResponse(
             json.dumps({"status": "server_error", "message": f"Wystąpił błąd serwera: {str(e)}"}),
             mimetype="application/json",
             status_code=500
        )