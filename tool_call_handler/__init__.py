import logging
import azure.functions as func
import os
import json
import requests
from openai import OpenAI


# === CONFIG ===
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PROXY_URL = os.environ.get("AZURE_PROXY_URL")

client = OpenAI(api_key=OPENAI_API_KEY)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("🔧 tool_call_handler triggered")

    # -------------------------------
    # 1. Parse request
    # -------------------------------
    try:
        body = req.get_json()
    except Exception as e:
        logging.error(f"❌ Invalid JSON: {e}")
        return func.HttpResponse("Invalid JSON", status_code=400)

    thread_id = body.get("thread_id")
    run_id = body.get("run_id")

    if not thread_id or not run_id:
        return func.HttpResponse("Missing thread_id or run_id", status_code=400)

    logging.info(f"➡️ Handling run {run_id} for thread {thread_id}")

    # -------------------------------
    # 2. Retrieve run
    # -------------------------------
    try:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
    except Exception as e:
        logging.error(f"❌ Failed to retrieve run: {e}")
        return func.HttpResponse("Failed to retrieve run", status_code=500)

    # If run does NOT require action → nothing to do
    if run.status != "requires_action":
        return func.HttpResponse("No action required", status_code=200)

    tool_calls = run.required_action.submit_tool_outputs.tool_calls

    outputs = []

    # -------------------------------
    # 3. Process tool calls
    # -------------------------------
    for call in tool_calls:
        function_name = call.function.name
        arguments = json.loads(call.function.arguments or "{}")

        logging.info(f"🔨 Tool invoked: {function_name}")
        logging.info(f"📦 Arguments: {arguments}")

        # Call proxy backend
        try:
            proxy_response = requests.post(PROXY_URL, json=arguments)
            proxy_text = proxy_response.text   # ALWAYS STRING
        except Exception as e:
            logging.error(f"❌ Proxy error: {e}")
            proxy_text = f"[Proxy error] {e}"

        # Normalize output → OpenAI REQUIRES a string
        if not isinstance(proxy_text, str):
            try:
                proxy_text = json.dumps(proxy_text)
            except:
                proxy_text = str(proxy_text)

        outputs.append({
            "tool_call_id": call.id,
            "output": proxy_text
        })

    # -------------------------------
    # 4. Submit tool outputs
    # -------------------------------
    try:
        client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=outputs
        )
        logging.info("✅ Tool outputs submitted")
    except Exception as e:
        logging.error(f"❌ Failed to submit tool outputs: {e}")
        return func.HttpResponse("Failed to submit tool outputs", status_code=500)

    return func.HttpResponse("OK", status_code=200)
