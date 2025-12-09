import logging
import json
import azure.functions as func
import os
from azure.storage.blob import BlobServiceClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('manage_files: Przetwarzanie żądania HTTP do zarządzania plikami.')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Proszę przesłać poprawny JSON.", status_code=400)

    operation = req_body.get('operation')
    source_name = req_body.get('source_name')
    target_name = req_body.get('target_name')
    prefix = req_body.get('prefix', '') # Opcjonalny argument dla 'list'

    if not operation:
        return func.HttpResponse("Brak wymaganego pola 'operation'.", status_code=400)

    try:
        connect_str = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
        container_name = os.environ["AZURE_BLOB_CONTAINER_NAME"]
        
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_client = blob_service_client.get_container_client(container_name)
        
        result_message = ""
        
        if operation == 'list':
            # Operacja 'list' z filtrem prefix (dla folderów np. 'custom_knowledge/')
            blob_list = container_client.list_blobs(name_starts_with=prefix)
            file_names = [blob.name for blob in blob_list]
            result_message = f"Pomyślnie pobrano listę {len(file_names)} plików z prefiksem '{prefix}'."
            response_data = {
                "operation": "list",
                "prefix": prefix,
                "files": file_names,
                "message": result_message
            }
        
        elif operation == 'delete':
            if not source_name:
                return func.HttpResponse("Brak 'source_name' dla operacji delete.", status_code=400)
            
            blob_client = container_client.get_blob_client(source_name)
            blob_client.delete_blob()
            result_message = f"Pomyślnie usunięto plik: {source_name}. Agent utrzymał czystość pamięci."
            response_data = {"operation": "delete", "source_name": source_name, "message": result_message}
            
        elif operation == 'rename':
            if not source_name or not target_name:
                return func.HttpResponse("Brak 'source_name' lub 'target_name' dla operacji rename.", status_code=400)
            
            # Rename w Blob Storage to 'copy' z nowego źródła + 'delete' starego
            source_blob_client = container_client.get_blob_client(source_name)
            target_blob_client = container_client.get_blob_client(target_name)
            
            target_blob_client.start_copy_from_url(source_blob_client.url)
            source_blob_client.delete_blob()
            
            result_message = f"Pomyślnie zmieniono nazwę pliku z '{source_name}' na '{target_name}' (operacja copy+delete). Agent zarchiwizował/zreorganizował wiedzę."
            response_data = {"operation": "rename", "source_name": source_name, "target_name": target_name, "message": result_message}

        else:
            return func.HttpResponse(f"Nieobsługiwana operacja: {operation}.", status_code=400)

        return func.HttpResponse(
            json.dumps(response_data, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        # Kod błędu 404 często oznacza, że blob nie istnieje (dla delete/rename)
        error_status = 500
        if "BlobNotFound" in str(e):
             error_status = 404
             
        logging.error(f"Błąd w manage_files: {e}")
        return func.HttpResponse(
             json.dumps({"error": f"Wystąpił błąd podczas operacji na Blob Storage (status: {error_status}): {str(e)}"}),
             mimetype="application/json",
             status_code=error_status
        )