import logging
import json
import azure.functions as func
from datetime import datetime, timezone

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('get_current_time: Przetwarzanie żądania HTTP.')
    
    try:
        # Pobieranie aktualnego czasu w formacie UTC (standard ISO 8601 z 'Z')
        now_utc = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        response_data = {
            "current_time_utc": now_utc,
            "message": "Pomyślnie pobrano aktualny czas UTC. Agent może go użyć do kontekstualizacji terminów (LO)."
        }
        
        return func.HttpResponse(
            json.dumps(response_data),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f"Błąd w get_current_time: {e}")
        return func.HttpResponse(
             json.dumps({"error": f"Wystąpił błąd serwera: {str(e)}"}),
             mimetype="application/json",
             status_code=500
        )