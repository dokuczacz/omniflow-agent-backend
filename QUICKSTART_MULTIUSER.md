# Quick Start - Multi-User Backend

## What Changed?

Your backend now supports **multi-user isolation**. Multiple people can use the same backend without accessing each other's data.

## How to Use

### 1. **Identify Your Users**
Each user needs a unique ID (can be any string):
- `alice_123`
- `user_bob`
- `project_team_001`

### 2. **Pass User ID to Functions**

Add this header to every API call:
```
X-User-Id: alice_123
```

**Full Example:**
```bash
curl -X POST https://your-backend.azurewebsites.net/api/add_new_data \
  -H "Content-Type: application/json" \
  -H "X-User-Id: alice_123" \
  -d '{
    "target_blob_name": "tasks.json",
    "new_entry": {
      "id": "T001",
      "content": "My task",
      "status": "open"
    }
  }'
```

### 3. **Data is Automatically Isolated**

Behind the scenes:
- **Alice's data** → `users/alice_123/tasks.json`
- **Bob's data** → `users/bob_456/tasks.json`
- They cannot see or access each other's files

## Integration with Your GPT

In your GPT system prompt (or Claude instructions), add:

```markdown
### User Isolation

When making calls to the backend functions, always include your unique user ID:

- Use the header: `X-User-Id: {user_id}`
- Where `{user_id}` is the person's unique identifier

This ensures your data is isolated from other users.

**Example:**
```
POST /api/add_new_data
Headers: X-User-Id: alice_123
Body: {
  "target_blob_name": "tasks.json",
  "new_entry": {...}
}
```

## All Functions Updated

✅ `read_blob_file` - Read user's file
✅ `list_blobs` - List user's files
✅ `add_new_data` - Add to user's file
✅ `get_filtered_data` - Query user's data

**Not yet updated** (coming soon):
- `update_data_entry`
- `remove_data_entry`
- `upload_data_or_file`
- `manage_files`

## Testing

### Test with Alice
```bash
# Add a task
curl -X POST http://localhost:7071/api/add_new_data \
  -H "X-User-Id: alice_123" \
  -H "Content-Type: application/json" \
  -d '{"target_blob_name": "tasks.json", "new_entry": {"id": "1", "text": "Alice task"}}'

# List blobs
curl -X GET "http://localhost:7071/api/list_blobs?user_id=alice_123"
```

### Test with Bob
```bash
# Add a task
curl -X POST http://localhost:7071/api/add_new_data \
  -H "X-User-Id: bob_456" \
  -H "Content-Type: application/json" \
  -d '{"target_blob_name": "tasks.json", "new_entry": {"id": "1", "text": "Bob task"}}'

# List blobs
curl -X GET "http://localhost:7071/api/list_blobs?user_id=bob_456"
```

## Backward Compatibility

If you don't provide a user ID:
- Defaults to `"default"` namespace
- All your existing data stays under `users/default/`
- Works exactly like before

## Key Files

| File | Purpose |
|------|---------|
| `shared/config.py` | Configuration & namespace management |
| `shared/user_manager.py` | Extract user IDs from requests |
| `shared/azure_client.py` | Azure client factory with user isolation |
| `USER_MANAGEMENT.md` | Full documentation |

## Need to Share with Someone?

1. Get their email or ID
2. Tell them to use: `X-User-Id: their_unique_id`
3. They immediately have isolated data access
4. No setup, no credentials, completely separate storage

---

See `USER_MANAGEMENT.md` for detailed documentation.
