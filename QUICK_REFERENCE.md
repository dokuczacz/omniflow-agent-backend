# Quick Reference - Data Extraction System

## 🚀 New API Endpoints

### Save Interaction
```bash
POST /api/save_interaction
Headers: X-User-Id: <user_id>

Body:
{
  "user_message": "string (required)",
  "assistant_response": "string (required)",
  "thread_id": "string (optional)",
  "tool_calls": [...] (optional),
  "metadata": {...} (optional)
}

Response:
{
  "status": "success",
  "interaction_id": "INT_20251211_130530_123456",
  "timestamp": "2025-12-11T13:05:30.123456Z",
  "total_interactions": 15,
  "storage_location": "users/test_user/interaction_logs.json"
}
```

### Get Interaction History
```bash
GET /api/get_interaction_history?limit=50&offset=0&thread_id=optional
Headers: X-User-Id: <user_id>

Response:
{
  "status": "success",
  "interactions": [...],
  "total_count": 100,
  "returned_count": 50,
  "offset": 0,
  "limit": 50
}
```

---

## 📝 Quick Test Commands

### Test 1: Save an Interaction
```bash
curl -X POST http://localhost:7071/api/save_interaction \
  -H "X-User-Id: alice_test" \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Show my tasks",
    "assistant_response": "You have 3 tasks",
    "thread_id": "thread_001"
  }'
```

### Test 2: Get History
```bash
curl "http://localhost:7071/api/get_interaction_history?limit=10" \
  -H "X-User-Id: alice_test"
```

### Test 3: Filter by Thread
```bash
curl "http://localhost:7071/api/get_interaction_history?thread_id=thread_001" \
  -H "X-User-Id: alice_test"
```

---

## 📦 What Gets Logged Automatically

When using `tool_call_handler`, the following is automatically logged:

✅ User message  
✅ Assistant response  
✅ Thread ID  
✅ All tool calls:
  - Tool name
  - Arguments
  - Results
  - Success/failure status  
✅ Timestamp  
✅ Metadata (assistant_id, source)

**No extra work needed!** Just use the tool_call_handler as normal.

---

## 🗂️ Storage Location

All interaction logs are stored in:
```
users/{user_id}/interaction_logs.json
```

Examples:
- `users/alice_test/interaction_logs.json`
- `users/bob_test/interaction_logs.json`
- `users/default/interaction_logs.json`

---

## ⚙️ Required Environment Variables

Add these to your Azure Function configuration:

```bash
FUNCTION_CODE_SAVE_INTERACTION=<your_function_key>
FUNCTION_CODE_GET_HISTORY=<your_function_key>
```

---

## 📊 Validation Limits

- **limit**: 1 to 1000 (default: 50)
- **offset**: ≥ 0 (default: 0)
- **thread_id**: optional string filter

---

## 🔒 Security

✅ User-isolated storage  
✅ Input validation  
✅ No cross-user access  
✅ Masked logging for sensitive data

---

## 📚 Full Documentation

- **TESTING_PLAN.md** - Complete testing scenarios (11 tests)
- **DATA_EXTRACTION_IMPLEMENTATION.md** - Technical details
- **IMPLEMENTATION_COMPLETE.md** - Implementation summary

---

## 🎯 Quick Start

1. **Deploy Functions**
   ```bash
   # Functions are ready to deploy
   func azure functionapp publish <your-function-app>
   ```

2. **Set Environment Variables**
   ```bash
   # In Azure Portal or via CLI
   az functionapp config appsettings set ...
   ```

3. **Test Basic Flow**
   ```bash
   # Send a message
   curl -X POST .../api/tool_call_handler \
     -d '{"message": "Add task: Buy milk", "user_id": "test"}'
   
   # Check it was logged
   curl ".../api/get_interaction_history?limit=1" \
     -H "X-User-Id: test"
   ```

4. **Follow Full Testing Plan**
   - See `TESTING_PLAN.md` for all 11 test scenarios

---

## 💡 Tips

- Interactions are logged **automatically** via tool_call_handler
- Use `thread_id` to track multi-turn conversations
- Logs grow over time - monitor storage
- Logging failures don't affect main functionality
- Each user has their own isolated logs

---

## 🆘 Troubleshooting

**Issue**: 401 Unauthorized  
**Fix**: Check function keys in environment variables

**Issue**: Interaction not saved  
**Fix**: Verify FUNCTION_CODE_SAVE_INTERACTION is set

**Issue**: Can't see history  
**Fix**: Verify X-User-Id header matches the user who saved interactions

**Issue**: 400 Bad Request on history  
**Fix**: Check limit (1-1000) and offset (≥0) parameters

---

## ✅ Ready to Use!

The data extraction system is complete and ready for UI testing.  
Start with **TESTING_PLAN.md** Test 5-11 to verify functionality.
