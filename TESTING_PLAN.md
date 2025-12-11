# UI Testing Plan - OmniFlow Agent Backend

## Overview
This document provides comprehensive testing scenarios for the OmniFlow Agent Backend system, including the new data extraction and interaction logging features.

---

## Table of Contents
1. [Test Environment Setup](#test-environment-setup)
2. [Core Data Management Tests](#core-data-management-tests)
3. [Interaction Logging Tests](#interaction-logging-tests)
4. [Multi-User Isolation Tests](#multi-user-isolation-tests)
5. [Tool Call Handler Tests](#tool-call-handler-tests)
6. [API Endpoint Reference](#api-endpoint-reference)

---

## Test Environment Setup

### Prerequisites
- Azure Functions running locally or deployed to Azure
- Access to Azure Blob Storage
- API testing tool (e.g., Postman, curl, or custom UI)

### Environment Variables Required
```bash
OPENAI_API_KEY=<your_openai_key>
OPENAI_ASSISTANT_ID=<your_assistant_id>
AZURE_PROXY_URL=<your_proxy_url>
FUNCTION_URL_BASE=<your_base_url>
AZURE_STORAGE_CONNECTION_STRING=<your_connection_string>
```

### Test Users
For multi-user testing, use these test user IDs:
- `alice_test_123` - Primary test user
- `bob_test_456` - Secondary test user
- `default` - Default/anonymous user

---

## Core Data Management Tests

### Test 1: Add New Data Entry
**Objective**: Verify that new data can be added to a JSON file with user isolation.

**Steps**:
1. Send POST request to `/api/add_new_data`
2. Include `X-User-Id: alice_test_123` header
3. Body:
```json
{
  "target_blob_name": "tasks.json",
  "new_entry": {
    "id": "T001",
    "title": "Test Task 1",
    "status": "pending",
    "created_at": "2025-12-11T10:00:00Z"
  }
}
```

**Expected Result**:
- Status: 200
- Response includes `entry_count` and `user_id`
- Data stored in `users/alice_test_123/tasks.json`

**UI Verification**:
- [ ] Request succeeds with 200 status
- [ ] Response shows correct user_id
- [ ] Entry count increments properly
- [ ] Data appears in user's blob storage

---

### Test 2: Read Blob File
**Objective**: Verify reading data with user isolation.

**Steps**:
1. Send GET request to `/api/read_blob_file`
2. Include `X-User-Id: alice_test_123` header
3. Query params: `?file_name=tasks.json`

**Expected Result**:
- Status: 200
- Returns array of entries for alice_test_123
- Does not return data from other users

**UI Verification**:
- [ ] Can retrieve previously added data
- [ ] Only user's data is returned
- [ ] JSON is properly formatted

---

### Test 3: List User Blobs
**Objective**: Verify listing files for a specific user.

**Steps**:
1. Send GET request to `/api/list_blobs`
2. Include `X-User-Id: alice_test_123` header

**Expected Result**:
- Status: 200
- Returns list of files in user's namespace
- Does not include other users' files

**UI Verification**:
- [ ] Shows all user files
- [ ] Excludes other users' files
- [ ] Handles empty results gracefully

---

### Test 4: Get Filtered Data
**Objective**: Verify filtering data by criteria.

**Steps**:
1. Add multiple entries with different statuses
2. Send POST to `/api/get_filtered_data`
3. Include `X-User-Id: alice_test_123` header
4. Body:
```json
{
  "target_blob_name": "tasks.json",
  "filter_key": "status",
  "filter_value": "pending"
}
```

**Expected Result**:
- Status: 200
- Returns only entries matching filter criteria

**UI Verification**:
- [ ] Filtering works correctly
- [ ] Returns only matching entries
- [ ] Handles no matches gracefully

---

## Interaction Logging Tests

### Test 5: Save Interaction
**Objective**: Verify interaction data is saved for analysis.

**Steps**:
1. Send POST request to `/api/save_interaction`
2. Include `X-User-Id: alice_test_123` header
3. Body:
```json
{
  "user_message": "What tasks do I have today?",
  "assistant_response": "You have 3 tasks pending for today.",
  "thread_id": "thread_abc123",
  "tool_calls": [
    {
      "tool_name": "get_filtered_data",
      "arguments": {"target_blob_name": "tasks.json", "filter_key": "due_date", "filter_value": "2025-12-11"},
      "result": {"status": "success", "count": 3},
      "status": "success"
    }
  ],
  "metadata": {
    "source": "ui_test"
  }
}
```

**Expected Result**:
- Status: 200
- Response includes `interaction_id` and `timestamp`
- Data stored in `users/alice_test_123/interaction_logs.json`

**UI Verification**:
- [ ] Interaction is saved successfully
- [ ] Unique interaction_id is generated
- [ ] Timestamp is accurate
- [ ] Total interaction count updates

---

### Test 6: Retrieve Interaction History
**Objective**: Verify retrieval of past interactions.

**Steps**:
1. Save multiple interactions (Test 5)
2. Send GET request to `/api/get_interaction_history`
3. Include `X-User-Id: alice_test_123` header
4. Optional query params: `?limit=10&offset=0`

**Expected Result**:
- Status: 200
- Returns list of interactions sorted by timestamp (newest first)
- Includes pagination info

**UI Verification**:
- [ ] Returns correct number of interactions
- [ ] Sorted by newest first
- [ ] Pagination works correctly
- [ ] All interaction fields are present

---

### Test 7: Filter Interactions by Thread
**Objective**: Verify filtering interactions by thread_id.

**Steps**:
1. Save interactions with different thread_ids
2. Send GET to `/api/get_interaction_history`
3. Include `X-User-Id: alice_test_123` header
4. Query param: `?thread_id=thread_abc123`

**Expected Result**:
- Status: 200
- Returns only interactions for specified thread

**UI Verification**:
- [ ] Filters correctly by thread_id
- [ ] Excludes interactions from other threads
- [ ] Returns accurate count

---

## Multi-User Isolation Tests

### Test 8: User Data Isolation
**Objective**: Verify complete data isolation between users.

**Steps**:
1. Add data for alice_test_123:
```json
{
  "target_blob_name": "notes.json",
  "new_entry": {"id": "N001", "content": "Alice's private note"}
}
```

2. Add data for bob_test_456:
```json
{
  "target_blob_name": "notes.json",
  "new_entry": {"id": "N001", "content": "Bob's private note"}
}
```

3. Read notes.json as alice_test_123
4. Read notes.json as bob_test_456

**Expected Result**:
- Alice only sees her note
- Bob only sees his note
- No cross-user data leakage

**UI Verification**:
- [ ] Alice's data is completely isolated
- [ ] Bob's data is completely isolated
- [ ] Same filename works for both users
- [ ] No cross-contamination

---

### Test 9: Interaction Log Isolation
**Objective**: Verify interaction logs are user-isolated.

**Steps**:
1. Save interactions for alice_test_123
2. Save interactions for bob_test_456
3. Retrieve history for alice_test_123
4. Retrieve history for bob_test_456

**Expected Result**:
- Each user only sees their own interactions
- No mixing of interaction logs

**UI Verification**:
- [ ] Alice sees only her interactions
- [ ] Bob sees only his interactions
- [ ] Interaction counts are separate

---

## Tool Call Handler Tests

### Test 10: Assistant with Tool Calls
**Objective**: Verify assistant can make tool calls and interactions are logged.

**Steps**:
1. Send POST to `/api/tool_call_handler`
2. Body:
```json
{
  "message": "Add a task: Buy groceries, due tomorrow",
  "user_id": "alice_test_123",
  "thread_id": null
}
```

**Expected Result**:
- Status: 200
- Assistant processes the message
- Tool call (add_new_data) is executed
- Interaction is automatically logged
- Response includes tool_calls_count

**UI Verification**:
- [ ] Message is processed successfully
- [ ] Tool calls execute correctly
- [ ] Response is coherent
- [ ] Interaction is logged automatically
- [ ] thread_id is returned for continuity

---

### Test 11: Multi-Turn Conversation
**Objective**: Verify conversation continuity and logging.

**Steps**:
1. First message: "Add a task: Buy milk"
2. Save returned thread_id
3. Second message: "What tasks do I have?" (use same thread_id)
4. Check interaction history

**Expected Result**:
- Both interactions use same thread_id
- History shows conversation flow
- Context is maintained between turns

**UI Verification**:
- [ ] Thread continuity works
- [ ] Both interactions are logged
- [ ] Context is preserved
- [ ] History shows conversation thread

---

## API Endpoint Reference

### Data Management Endpoints

#### POST /api/add_new_data
Add a new entry to a JSON array.
- Headers: `X-User-Id: <user_id>`
- Body: `{ "target_blob_name": "file.json", "new_entry": {...} }`

#### GET /api/read_blob_file
Read file contents.
- Headers: `X-User-Id: <user_id>`
- Query: `?file_name=file.json`

#### GET /api/list_blobs
List all files for user.
- Headers: `X-User-Id: <user_id>`

#### POST /api/get_filtered_data
Get filtered data from file.
- Headers: `X-User-Id: <user_id>`
- Body: `{ "target_blob_name": "file.json", "filter_key": "key", "filter_value": "value" }`

#### POST /api/update_data_entry
Update existing entry.
- Headers: `X-User-Id: <user_id>`
- Body: `{ "target_blob_name": "file.json", "find_key": "id", "find_value": "123", "update_key": "status", "update_value": "done" }`

#### POST /api/remove_data_entry
Remove entry from file.
- Headers: `X-User-Id: <user_id>`
- Body: `{ "target_blob_name": "file.json", "key_to_find": "id", "value_to_find": "123" }`

### Interaction Logging Endpoints

#### POST /api/save_interaction
Save interaction data for analysis.
- Headers: `X-User-Id: <user_id>`
- Body:
```json
{
  "user_message": "string",
  "assistant_response": "string",
  "thread_id": "string (optional)",
  "tool_calls": [...],
  "metadata": {...}
}
```

#### GET /api/get_interaction_history
Retrieve interaction history.
- Headers: `X-User-Id: <user_id>`
- Query: `?thread_id=<optional>&limit=50&offset=0`

### Assistant Endpoints

#### POST /api/tool_call_handler
Chat with assistant (includes automatic logging).
- Body:
```json
{
  "message": "string",
  "user_id": "string",
  "thread_id": "string (optional)"
}
```

#### POST /api/proxy_router
Route tool calls to appropriate functions.
- Body:
```json
{
  "action": "action_name",
  "params": {...}
}
```

---

## Success Criteria

### Functional Requirements
- [ ] All data operations work correctly
- [ ] User isolation is maintained
- [ ] Interaction logging works automatically
- [ ] History retrieval works with filters
- [ ] Assistant tool calls execute properly

### Non-Functional Requirements
- [ ] Response times < 2 seconds for reads
- [ ] Response times < 5 seconds for writes
- [ ] No data corruption
- [ ] Proper error handling
- [ ] Clear error messages

### Security Requirements
- [ ] Users cannot access other users' data
- [ ] User IDs are validated
- [ ] No namespace injection vulnerabilities
- [ ] Interaction logs are properly isolated

---

## Test Execution Checklist

### Pre-Testing
- [ ] Environment variables configured
- [ ] Azure Functions running
- [ ] Azure Blob Storage accessible
- [ ] Test users created

### During Testing
- [ ] Document all test results
- [ ] Screenshot any UI issues
- [ ] Note response times
- [ ] Track any errors or warnings

### Post-Testing
- [ ] Clean up test data (optional)
- [ ] Document any bugs found
- [ ] Verify all critical paths work
- [ ] Confirm security measures effective

---

## Sample Test Data

### Sample Tasks
```json
[
  {
    "id": "T001",
    "title": "Complete project proposal",
    "status": "in_progress",
    "priority": "high",
    "due_date": "2025-12-15",
    "created_at": "2025-12-11T10:00:00Z"
  },
  {
    "id": "T002",
    "title": "Review code changes",
    "status": "pending",
    "priority": "medium",
    "due_date": "2025-12-12",
    "created_at": "2025-12-11T11:00:00Z"
  },
  {
    "id": "T003",
    "title": "Team meeting",
    "status": "completed",
    "priority": "low",
    "due_date": "2025-12-11",
    "created_at": "2025-12-11T09:00:00Z"
  }
]
```

### Sample Notes
```json
[
  {
    "id": "N001",
    "title": "Meeting notes",
    "content": "Discussed Q4 objectives...",
    "tags": ["meeting", "planning"],
    "created_at": "2025-12-11T14:00:00Z"
  },
  {
    "id": "N002",
    "title": "Research findings",
    "content": "Found interesting approach to...",
    "tags": ["research", "development"],
    "created_at": "2025-12-11T15:30:00Z"
  }
]
```

---

## Troubleshooting Guide

### Common Issues

**Issue**: 401 Unauthorized
- **Solution**: Check function keys in environment variables

**Issue**: 404 Not Found on blob
- **Solution**: Verify user_id and file_name are correct

**Issue**: 500 Internal Server Error
- **Solution**: Check Azure Functions logs for detailed error

**Issue**: Cross-user data visible
- **Solution**: Verify X-User-Id header is being sent correctly

**Issue**: Interaction not logged
- **Solution**: Check FUNCTION_CODE_SAVE_INTERACTION is set

---

## Conclusion

This testing plan covers all critical functionality of the OmniFlow Agent Backend, including:
- ✅ Core data management operations
- ✅ New interaction logging features
- ✅ Multi-user isolation
- ✅ Assistant tool call integration
- ✅ Security and data isolation

Complete all tests to ensure the system is production-ready and the UI functions correctly.
