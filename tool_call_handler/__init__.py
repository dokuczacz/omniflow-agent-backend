import logging
import azure.functions as func
import os
import json
import requests
import time
from typing import Optional
from openai import OpenAI

# === CONFIGURATION ===
OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
PROXY_URL: str = os.environ.get("AZURE_PROXY_URL", "")
ASSISTANT_ID: str = os.environ.get("OPENAI_ASSISTANT_ID", "")
MAX_RETRIES: int = 5
POLL_INTERVAL: float = 1.0

if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in environment variables.")
if not PROXY_URL:
    raise ValueError("Missing AZURE_PROXY_URL in environment variables.")
if not ASSISTANT_ID:
    raise ValueError("Missing OPENAI_ASSISTANT_ID in environment variables.")

client = OpenAI(api_key=OPENAI_API_KEY)



def execute_tool_call(tool_name: str, tool_input: dict) -> str:
    """
    Execute a tool call via proxy_router.
    
    Args:
        tool_name: Name of the tool (e.g., "list_blobs", "read_blob_file")
        tool_input: Parameters for the tool
        
    Returns:
        Tool result as JSON string
    """
    try:
        payload = {
            "action": tool_name,
            "params": tool_input
        }
        
        logging.info(f"🔨 Executing tool: {tool_name} | Input: {tool_input}")
        
        response = requests.post(PROXY_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        logging.info(f"✅ Tool result: {result}")
        
        return json.dumps(result)
    except Exception as e:
        logging.error(f"❌ Tool execution failed: {e}")
        return json.dumps({"error": str(e)})


def poll_run_until_completion(thread_id: str, run_id: str) -> dict:
    """
    Poll OpenAI run until it's complete or requires action.
    Handle all tool calls that come up.
    
    Args:
        thread_id: Thread ID
        run_id: Run ID
        
    Returns:
        Final run object
    """
    retry_count = 0
    
    while retry_count < MAX_RETRIES:
        try:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            
            logging.info(f"🔍 Run status: {run.status}")
            
            # === If run requires tool calls ===
            if run.status == "requires_action":
                logging.info("🛠️ Assistant requires tool calls")
                
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                outputs = []
                
                # Execute each tool call
                for call in tool_calls:
                    function_name = call.function.name
                    arguments = json.loads(call.function.arguments or "{}")
                    
                    logging.info(f"🔧 Tool call: {function_name} | Args: {arguments}")
                    
                    # Execute via proxy
                    tool_result = execute_tool_call(function_name, arguments)
                    
                    outputs.append({
                        "tool_call_id": call.id,
                        "output": tool_result
                    })
                
                # Submit tool outputs back to OpenAI
                logging.info(f"📤 Submitting {len(outputs)} tool outputs")
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run_id,
                    tool_outputs=outputs
                )
                
                # Continue polling
                time.sleep(POLL_INTERVAL)
                retry_count += 1
                continue
            
            # === If run is completed ===
            elif run.status == "completed":
                logging.info("✅ Run completed successfully")
                return run
            
            # === If run failed ===
            elif run.status in ["failed", "cancelled", "expired"]:
                logging.error(f"❌ Run {run.status}")
                return run
            
            # === Still in progress ===
            else:
                logging.info(f"⏳ Run in progress ({run.status}), polling...")
                time.sleep(POLL_INTERVAL)
                retry_count += 1
                continue
                
        except Exception as e:
            logging.error(f"❌ Error polling run: {e}")
            retry_count += 1
            time.sleep(POLL_INTERVAL)
    
    raise Exception(f"Max retries ({MAX_RETRIES}) reached while polling run")


def get_assistant_response(thread_id: str) -> str:
    """
    Retrieve the latest assistant message from the thread.
    
    Args:
        thread_id: Thread ID
        
    Returns:
        Assistant's text response
    """
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    
    for msg in messages.data:
        if msg.role == "assistant":
            # Extract text from content blocks
            for content in msg.content:
                if hasattr(content, "text"):
                    return content.text.value
    
    return "No response from assistant."
    

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main handler: Create thread, send message, orchestrate tool calls, return response.
    
    Expected JSON input:
    {
        "message": "user message",
        "user_id": "alice_123",
        "thread_id": "thread_xyz" (optional - reuse existing thread)
    }
    """
    logging.info("🚀 tool_call_handler triggered")
    
    try:
        body = req.get_json()
    except Exception as e:
        logging.error(f"❌ Invalid JSON: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON payload"}),
            status_code=400,
            mimetype="application/json"
        )
    
    user_message = body.get("message", "")
    user_id = body.get("user_id", "default")
    thread_id = body.get("thread_id", "")
    
    if not user_message:
        return func.HttpResponse(
            json.dumps({"error": "Missing 'message' field"}),
            status_code=400,
            mimetype="application/json"
        )
    
    try:
        # === Step 1: Create or retrieve thread ===
        if not thread_id:
            logging.info(f"📌 Creating new thread for user: {user_id}")
            thread = client.beta.threads.create()
            thread_id = thread.id
            logging.info(f"✅ Thread created: {thread_id}")
        else:
            logging.info(f"📌 Reusing thread: {thread_id}")
        
        # === Step 2: Add user message to thread ===
        logging.info(f"💬 Adding message: {user_message}")
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )
        
        # === Step 3: Create a run with the assistant ===
        logging.info(f"🔄 Creating run with assistant: {ASSISTANT_ID}")
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )
        run_id = run.id
        logging.info(f"✅ Run created: {run_id}")
        
        # === Step 4: Poll until completion (handles tool calls) ===
        logging.info("⏳ Polling run for completion...")
        final_run = poll_run_until_completion(thread_id, run_id)
        
        # === Step 5: Get assistant's final response ===
        logging.info("📖 Retrieving assistant response...")
        assistant_response = get_assistant_response(thread_id)
        
        # === Step 6: Return response with thread info ===
        response_data = {
            "status": "success",
            "thread_id": thread_id,
            "run_id": run_id,
            "user_id": user_id,
            "response": assistant_response,
            "run_status": final_run.status
        }
        
        logging.info(f"✅ Handler completed successfully")
        return func.HttpResponse(
            json.dumps(response_data, ensure_ascii=False),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"❌ Critical error: {e}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "error": str(e)
            }, ensure_ascii=False),
            status_code=500,
            mimetype="application/json"
        )

