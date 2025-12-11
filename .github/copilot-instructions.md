# Copilot Coding Agent Guidelines

## Repository Overview

This is the **OmniFlow Agent Backend** - a production-ready Azure Functions backend built with Python 3.12 that provides multi-user data isolation capabilities. The backend enables multiple users, GPT instances, or clients to share a single backend infrastructure while maintaining complete data separation through automatic namespacing.

### Key Features
- Multi-user data isolation using Azure Blob Storage namespacing
- RESTful API endpoints for data management
- User ID extraction from headers, query parameters, or request body
- Automatic namespace injection for secure data separation
- Singleton pattern for efficient Azure client management

## Technology Stack

- **Runtime**: Python 3.12+
- **Framework**: Azure Functions v2 programming model (Python)
- **Storage**: Azure Blob Storage
- **Dependencies**:
  - `azure-functions` - Azure Functions framework
  - `azure-storage-blob` - Azure Blob Storage SDK
  - `requests` - HTTP library
  - `openai>=1.20.0` - OpenAI API client
  - `pydantic==1.10.13` - Data validation

## Project Architecture

### Directory Structure

```
omniflow-agent-backend/
├── .github/                    # GitHub configuration
│   └── copilot-instructions.md # This file
├── shared/                     # Shared utilities module
│   ├── __init__.py            # Package initialization
│   ├── config.py              # Configuration & namespace logic
│   ├── user_manager.py        # User extraction & validation
│   └── azure_client.py        # Azure Blob client factory
├── add_new_data/              # Function: Add entries to JSON arrays
├── read_blob_file/            # Function: Read blob content
├── list_blobs/                # Function: List user's blobs
├── get_filtered_data/         # Function: Query user's data
├── update_data_entry/         # Function: Update existing entries
├── remove_data_entry/         # Function: Remove entries
├── upload_data_or_file/       # Function: Upload files
├── manage_files/              # Function: File management
├── tool_call_handler/         # Function: Handle tool calls
├── get_current_time/          # Function: Get current time
├── proxy_router/              # Function: Route proxy requests
├── function_app.py            # Main Azure Functions app
├── host.json                  # Azure Functions host config
├── requirements.txt           # Python dependencies
└── [Documentation files]      # Various .md documentation
```

### User Namespace Pattern

All user data follows this structure:
```
users/{user_id}/{file_name}
```

Examples:
- `users/alice_123/tasks.json`
- `users/bob_456/ideas.json`
- `users/default/knowledge.json` (default namespace)

## Coding Standards

### Python Style Guide

1. **Follow PEP 8** conventions for Python code
2. **Type Hints**: Use type hints from the `typing` module where applicable
3. **Docstrings**: Use docstrings for all functions and classes, following Google style:
   ```python
   def function_name(param1: str, param2: int) -> dict:
       """
       Brief description of function.
       
       Args:
           param1: Description of param1
           param2: Description of param2
           
       Returns:
           Description of return value
       """
   ```

4. **Import Organization**:
   ```python
   # Standard library imports
   import logging
   import json
   
   # Third-party imports
   import azure.functions as func
   from azure.core.exceptions import ResourceNotFoundError
   
   # Local imports
   from shared.azure_client import AzureBlobClient
   from shared.user_manager import extract_user_id
   ```

5. **Error Handling**: Always use specific exception types, never bare `except:`
6. **Logging**: Use Python's `logging` module with appropriate log levels
7. **JSON Formatting**: Use `json.dumps()` with `indent=2` and `ensure_ascii=False` for better readability

### Azure Functions Patterns

Every Azure Function must follow this pattern:

```python
import logging
import json
import azure.functions as func
from azure.core.exceptions import ResourceNotFoundError, AzureError
import sys
import os

# Add parent directory to path for shared imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.azure_client import AzureBlobClient
from shared.user_manager import extract_user_id


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Function description with user isolation.
    
    Parameters (in JSON body or query string):
    - param_name (required/optional): Description
    - user_id (optional): User ID (extracted from header/query/body)
    
    Returns:
    - Success response with result
    """
    logging.info('function_name: Processing HTTP request with user isolation')
    
    # 1. Parse request and extract parameters
    
    # 2. Extract user ID from request (ALWAYS include this)
    user_id = extract_user_id(req)
    logging.info(f"function_name: user_id={user_id}, ...")
    
    # 3. Get blob client with user isolation
    blob_client = AzureBlobClient.get_blob_client(blob_name, user_id)
    
    # 4. Perform operation on user-scoped blob
    
    # 5. Return response (ALWAYS include user_id in response)
    return func.HttpResponse(
        json.dumps({
            "status": "success",
            "user_id": user_id,
            # ... other response fields
        }),
        status_code=200,
        mimetype="application/json"
    )
```

### Security Best Practices

1. **User Isolation**: ALWAYS use `extract_user_id(req)` to get user ID from requests
2. **Namespace Injection**: ALWAYS use `AzureBlobClient.get_blob_client(name, user_id)` to ensure proper namespacing
3. **Input Validation**: Validate all user inputs before processing
4. **No Secrets in Code**: Use environment variables for sensitive data (accessed via `shared/config.py`)
5. **Error Messages**: Never expose internal details or stack traces to users
6. **Cross-User Access**: Never allow direct access to blob names without user_id validation

### User ID Extraction Priority

User IDs are extracted in this order:
1. HTTP Header: `X-User-Id` (RECOMMENDED)
2. Query Parameter: `user_id` or `userId`
3. Request Body (JSON): `user_id` or `userId`
4. Default: `"default"` if none provided

Valid user IDs:
- Must be 3-64 characters long
- Alphanumeric plus underscore, hyphen, or dot only
- Examples: `alice_123`, `user-456`, `team.project`

## Build and Test Instructions

### Local Development Setup

1. **Prerequisites**:
   - Python 3.12 or higher
   - Azure Functions Core Tools
   - Azure Storage Emulator (Azurite) for local development

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Local Development with Azurite**:
   ```bash
   # Start Azurite (Azure Storage Emulator)
   # The default connection string in config.py points to local Azurite
   
   # Start Azure Functions locally
   func start
   ```

4. **Testing Endpoints**:
   ```bash
   # Test with user ID in header (recommended)
   curl -X POST http://localhost:7071/api/add_new_data \
     -H "Content-Type: application/json" \
     -H "X-User-Id: test_user_123" \
     -d '{"target_blob_name":"tasks.json","new_entry":{"id":"1","text":"Test task"}}'
   
   # Test user isolation
   curl "http://localhost:7071/api/list_blobs?user_id=test_user_123"
   ```

### Testing Guidelines

- **Manual Testing**: Test user isolation by creating data for different user IDs and verifying separation
- **Test Endpoints**: Use curl or Postman to test HTTP endpoints
- **Verify User Namespace**: Check that blobs are created under `users/{user_id}/` prefix
- **Error Scenarios**: Test with missing parameters, invalid JSON, and unauthorized access

### Deployment

The backend is designed for Azure Functions deployment:
- Use Azure Functions deployment methods (VS Code extension, Azure CLI, or CI/CD)
- Set environment variables in Azure Functions configuration
- Ensure Azure Blob Storage container exists before deployment

## Environment Variables

Configure these in `local.settings.json` (local) or Azure Functions Application Settings (production):

- `AZURE_STORAGE_CONNECTION_STRING`: Azure Storage connection string (defaults to Azurite for local dev)
- `AZURE_BLOB_CONTAINER_NAME`: Container name (default: `agent-knowledge-base`)
- `OPENAI_API_KEY`: OpenAI API key (if using OpenAI features)
- `PROXY_URL`: Proxy URL (if needed)

## Common Tasks and Patterns

### Adding a New Azure Function

1. Create a new directory with function name
2. Add `__init__.py` with the main function following the standard pattern
3. Add `function.json` with trigger configuration
4. Import shared utilities from `shared/` module
5. Always include user isolation via `extract_user_id(req)`
6. Always use `AzureBlobClient.get_blob_client(name, user_id)` for blob operations

### Modifying Existing Functions

1. Maintain the existing pattern and structure
2. Preserve user isolation logic
3. Update docstrings if changing parameters or behavior
4. Test with multiple user IDs to verify isolation

### Working with Shared Utilities

- `shared/config.py`: Configuration and namespace generation
- `shared/user_manager.py`: User ID extraction and validation
- `shared/azure_client.py`: Azure Blob Storage client factory

These are singleton modules - modifications affect all functions.

## Documentation Requirements

- **Code Changes**: Update relevant .md files if changing architecture or patterns
- **API Changes**: Document new parameters or response formats in function docstrings
- **Architecture Changes**: Update ARCHITECTURE.md and USER_MANAGEMENT.md
- **New Features**: Add examples to documentation files

## Domain-Specific Knowledge

### Multi-User Isolation System

This backend implements a **namespace-based isolation system**:
- Each user's data is stored under `users/{user_id}/` prefix
- No cross-user data access is possible
- Default namespace is `users/default/` for backward compatibility
- User namespacing is automatic and transparent to clients

### Data Storage Patterns

- **JSON Arrays**: Most data stored as JSON arrays in blobs
- **File Operations**: Support for both JSON data and arbitrary files
- **Atomic Operations**: Blob operations are atomic at the blob level
- **Concurrent Access**: Azure Blob Storage handles concurrent access

### Interaction Logging

The `tool_call_handler` function logs all assistant interactions to `users/{user_id}/interaction_logs.json` with complete data model including:
- Timestamp
- Tool name
- Parameters
- Results
- User context

## Task Guidelines for Copilot

### When Making Changes

1. **Minimal Changes**: Make the smallest possible changes to achieve the goal
2. **Preserve Patterns**: Follow existing code patterns and structure
3. **User Isolation**: Never bypass or remove user isolation logic
4. **Test Isolation**: Always test that changes maintain data separation between users
5. **Security First**: Ensure changes don't introduce security vulnerabilities

### What to Prioritize

- Code consistency with existing patterns
- Maintaining user data isolation
- Clear error messages and logging
- Proper type hints and docstrings
- Backward compatibility where possible

### What to Avoid

- Removing or modifying user isolation logic
- Adding unnecessary dependencies
- Creating security vulnerabilities
- Breaking backward compatibility unnecessarily
- Exposing internal errors to end users
- Modifying files in `.github/agents/` directory (these are for other agents)

## Additional Resources

- **00_START_HERE.md**: Complete overview of the multi-user implementation
- **USER_MANAGEMENT.md**: Detailed user isolation documentation
- **ARCHITECTURE.md**: System architecture diagrams and data flow
- **QUICKSTART_MULTIUSER.md**: Quick start guide for multi-user features

## Notes for Copilot Agent

- This repository uses Azure Functions v2 programming model (Python)
- All functions must maintain user isolation via the shared utilities
- The singleton pattern in `azure_client.py` is critical for performance
- User IDs are extracted automatically; never require manual specification in function logic
- All blob operations must go through `AzureBlobClient` to ensure proper namespacing
- When in doubt about patterns, refer to existing function implementations like `add_new_data` or `read_blob_file`
