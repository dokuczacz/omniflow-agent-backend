import logging
import azure.functions as func
import os
import json
import time
from openai import OpenAI

# === CONFIGURATION ===
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ASSISTANT_ID = os.environ.get("OPENAI_ASSISTANT_ID", "")
PROXY_URL = os.environ.get("AZURE_PROXY_URL", "")

if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY")
if not ASSISTANT_ID:
    raise ValueError("Missing OPENAI_ASSISTANT_ID")
if not PROXY_URL:
    raise ValueError("Missing AZURE_PROXY_URL")

client = OpenAI(api_key=OPENAI_API_KEY)

# === PHASE 2: CHAT WITH TOOL SUPPORT ===

def execute_tool_call(tool_name: str, tool_arguments: dict) -> str:
    """Execute a tool via proxy_router"""
    import requests
    
    try:
        payload = {
            "action": tool_name,
            "params": tool_arguments
        }
        logging.info(f"Executing tool: {tool_name} with args: {tool_arguments}")
        
        response = requests.post(PROXY_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        logging.info(f"Tool result: {result}")
        
        return json.dumps(result)
    except Exception as e:
        logging.error(f"Tool execution failed: {e}")
        return json.dumps({"error": str(e)})

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Phase 2: Chat with tool support
    Input: {"message": "...", "user_id": "...", "thread_id": "..." (optional)}
    Output: {"response": "...", "thread_id": "...", "status": "success"}
    """
    logging.info("=== tool_call_handler: Phase 2 - Chat with Tools ===")
    
    try:
        body = req.get_json()
        logging.info(f"Received body: {json.dumps(body, indent=2)}")
    except Exception as e:
        logging.error(f"Invalid JSON: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON payload"}),
            status_code=400,
            mimetype="application/json"
        )
    
    user_message = body.get("message", "")
    user_id = body.get("user_id", "default")
    thread_id = body.get("thread_id")
    
    if not user_message:
        return func.HttpResponse(
            json.dumps({"error": "Missing 'message' field"}),
            status_code=400,
            mimetype="application/json"
        )
    
    try:
        # Step 1: Create or reuse thread
        if not thread_id:
            logging.info(f"Creating new thread for user: {user_id}")
            thread = client.beta.threads.create()
            thread_id = thread.id
            logging.info(f"Thread created: {thread_id}")
        else:
            logging.info(f"Reusing thread: {thread_id}")
        
        # Step 2: Add user message
        logging.info(f"Adding message: {user_message}")
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )
        
        # Step 3: Create run
        logging.info(f"Creating run with assistant: {ASSISTANT_ID}")
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )
        logging.info(f"Run created: {run.id}, status: {run.status}")
        
        # Step 4: Poll until complete (with exponential backoff)
        logging.info("Polling for completion with exponential backoff...")
        max_attempts = 40
        wait_times = [0.5, 0.5, 0.5, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 5, 5] * 2  # Up to ~120 seconds with longer waits
        
        for attempt, wait_duration in enumerate(wait_times[:max_attempts]):
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            logging.info(f"Poll {attempt+1}: status = {run.status} (waited {wait_duration}s)")
            
            if run.status == "completed":
                logging.info("Run completed!")
                break
            elif run.status == "failed":
                logging.error(f"Run failed: {run.last_error}")
                return func.HttpResponse(
                    json.dumps({"error": f"Run failed: {run.last_error}"}),
                    status_code=500,
                    mimetype="application/json"
                )
            elif run.status == "requires_action":
                # PHASE 2: Handle tool calls
                logging.info("Run requires action - handling tool calls")
                
                if not run.required_action or not hasattr(run.required_action, "submit_tool_outputs"):
                    logging.error("No tool outputs found in required_action")
                    return func.HttpResponse(
                        json.dumps({"error": "Invalid requires_action state"}),
                        status_code=500,
                        mimetype="application/json"
                    )
                
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                outputs = []
                
                for call in tool_calls:
                    function_name = call.function.name
                    arguments = json.loads(call.function.arguments or "{}")
                    
                    logging.info(f"Tool call: {function_name}({arguments})")
                    
                    # Execute tool via proxy
                    tool_result = execute_tool_call(function_name, arguments)
                    
                    outputs.append({
                        "tool_call_id": call.id,
                        "output": tool_result
                    })
                
                # Submit tool outputs
                logging.info(f"Submitting {len(outputs)} tool outputs")
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=outputs
                )
                
                # Continue polling after submitting outputs
                time.sleep(wait_duration)
                continue
            
            time.sleep(wait_duration)
        
        # Step 5: Get assistant response
        logging.info("Retrieving assistant response...")
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        
        assistant_response = None
        for msg in messages.data:
            if msg.role == "assistant":
                for content in msg.content:
                    if hasattr(content, "text"):
                        assistant_response = content.text.value
                        break
                break
        
        if not assistant_response:
            assistant_response = "No response from assistant."
        
        logging.info(f"Assistant response: {assistant_response}")
        
        # Step 6: Return response
        response_data = {
            "status": "success",
            "response": assistant_response,
            "thread_id": thread_id,
            "user_id": user_id
        }
        
        return func.HttpResponse(
            json.dumps(response_data, ensure_ascii=False),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Critical error: {e}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

