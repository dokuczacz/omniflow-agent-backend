# UI Testing Instructions for Streamlit Simple Interface

## Overview
This document provides comprehensive testing instructions for the simplified OmniFlow Assistant UI (`streamlit_simple.py`).

## Prerequisites
1. Ensure you have Python 3.8+ installed
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables:
   - `AZURE_FUNCTION_KEY`: Your Azure Function authentication key
   - (Optional) `OPENAI_API_KEY`: For additional features

## Starting the UI

```bash
streamlit run streamlit_simple.py
```

The UI will open in your browser at `http://localhost:8501`

## Testing Checklist

### 1. Initial Load
- [ ] Page loads without errors
- [ ] Title "🚀 OmniFlow Assistant" is displayed
- [ ] Debug panel is collapsed by default
- [ ] Backend status shows "Unknown" initially
- [ ] Avg Response time shows "0.00s"
- [ ] Messages counter shows "0"

### 2. Configuration Panel (Sidebar)
- [ ] Sidebar is visible on the left
- [ ] User ID input field is present with default value "default_user"
- [ ] Category dropdown is present
- [ ] Can change User ID value
- [ ] Can select different categories: TM, PS, LO, GEN, ID, PE, UI, ML, SYS

### 3. Debug Panel (Collapsed)
- [ ] Click "🔍 Debug Panel" to expand
- [ ] Three tabs are visible: "📊 Response Times", "📝 Debug Logs", "ℹ️ System Info"

#### Response Times Tab
- [ ] Shows "No data yet" initially
- [ ] After API call, shows timestamp, endpoint name, and response time
- [ ] Shows up to 5 most recent response times
- [ ] Times are displayed in seconds with 2 decimal places

#### Debug Logs Tab
- [ ] Shows "No logs yet" initially
- [ ] After actions, shows colored log entries (🔵 INFO, 🟢 SUCCESS, 🔴 ERROR)
- [ ] Logs show timestamp, level, and message
- [ ] Shows up to 10 most recent logs
- [ ] Logs are in reverse chronological order (newest first)

#### System Info Tab
- [ ] Displays User ID
- [ ] Displays selected Category
- [ ] Displays Thread ID (None initially, then UUID after first message)
- [ ] Displays Backend URL
- [ ] Displays Total Messages count

### 4. Backend Status Indicators (Top Metrics)
- [ ] Backend status changes from "Unknown" to "✅ Connected" after successful API call
- [ ] Backend status changes to "❌ Error" when API call fails
- [ ] Avg Response metric updates after each API call
- [ ] Messages counter increments with each message (user + assistant)
- [ ] Last Error displays when there's an error (red error box)

### 5. Chat Interface

#### Sending Messages
- [ ] Chat input field is visible at the bottom
- [ ] Placeholder text: "Type your message here..."
- [ ] Type a message and press Enter
- [ ] User message appears in chat with "user" avatar
- [ ] Spinner appears: "🤔 Thinking..."
- [ ] Assistant response appears with "assistant" avatar
- [ ] Chat automatically scrolls to show newest messages

#### Message Display
- [ ] User messages are distinguishable from assistant messages
- [ ] Messages display full content
- [ ] Long messages wrap properly
- [ ] Emoji and special characters display correctly

#### Multiple Messages
- [ ] Send 3-5 messages in sequence
- [ ] All messages remain visible
- [ ] Chat history is maintained during session
- [ ] Messages are in correct chronological order

### 6. Error Handling

#### Network Errors
- [ ] Disconnect network or use invalid FUNCTION_KEY
- [ ] Send a message
- [ ] Backend status shows "❌ Error"
- [ ] Error appears in Last Error metric
- [ ] Error log appears in Debug Logs with 🔴 ERROR
- [ ] User receives error message in chat

#### Timeout Testing
- [ ] Test with slow network
- [ ] Verify 30-second timeout is respected
- [ ] Error is properly displayed

### 7. Response Time Tracking
- [ ] Send multiple messages
- [ ] Open Debug Panel → Response Times tab
- [ ] Verify each API call is logged with:
  - Timestamp
  - Endpoint name (tool_call_handler)
  - Response time in seconds
- [ ] Verify Avg Response metric matches average of logged times
- [ ] Verify only last 5 calls are kept

### 8. Debug Logging
- [ ] Perform various actions (send messages, etc.)
- [ ] Open Debug Panel → Debug Logs tab
- [ ] Verify logs show:
  - 🔵 INFO: "Calling tool_call_handler..."
  - 🟢 SUCCESS: "tool_call_handler completed in X.XXs"
  - 🔴 ERROR: (when errors occur)
- [ ] Verify timestamps are correct
- [ ] Verify only last 10 logs are kept

### 9. Session Persistence
- [ ] Send several messages
- [ ] Refresh the browser page (F5)
- [ ] Verify messages are cleared (expected - session state resets)
- [ ] Verify User ID and Category persist from browser cache

### 10. UI Responsiveness
- [ ] Resize browser window
- [ ] Verify layout adjusts appropriately
- [ ] Test on different screen sizes if possible
- [ ] Verify all elements remain accessible

### 11. Footer Information
- [ ] Footer displays: "OmniFlow Assistant | User: [user_id] | Category: [category] | [current datetime]"
- [ ] User ID matches sidebar input
- [ ] Category matches sidebar selection
- [ ] Datetime updates on page refresh

## Test Scenarios

### Scenario A: First-Time User
1. Open UI for the first time
2. Keep default User ID
3. Select a category
4. Send a simple message: "Hello"
5. Verify response is received
6. Check Debug Panel for metrics

### Scenario B: Multiple Conversations
1. Set User ID to "test_user_123"
2. Select category "TM"
3. Send message: "What tasks do I have?"
4. Wait for response
5. Send follow-up: "Add a new task"
6. Verify thread_id persists across messages
7. Check response times are logged

### Scenario C: Error Recovery
1. Set invalid FUNCTION_KEY in environment
2. Restart UI
3. Send a message
4. Verify error is displayed properly
5. Check error appears in debug logs
6. Set correct FUNCTION_KEY
7. Restart UI
8. Verify connection works

### Scenario D: Category Switching
1. Start with category "TM"
2. Send a message
3. Change category to "PS"
4. Send another message
5. Verify both messages work with different categories

### Scenario E: Debug Panel Usage
1. Collapse and expand debug panel multiple times
2. Switch between all three tabs
3. Verify all data displays correctly
4. Send messages while debug panel is open
5. Verify metrics update in real-time

## Expected Behavior

### Success Indicators
- ✅ Backend Status: "✅ Connected"
- ✅ Response times: < 5 seconds typically
- ✅ Messages appear promptly
- ✅ No console errors in browser
- ✅ Debug logs show SUCCESS entries

### Failure Indicators
- ❌ Backend Status: "❌ Error"
- ❌ Error messages in chat
- ❌ Red error box at top
- ❌ ERROR entries in debug logs
- ❌ No response from assistant

## Troubleshooting

### UI Won't Start
- Check Python version: `python --version`
- Reinstall dependencies: `pip install -r requirements.txt`
- Check port 8501 is not in use

### Backend Connection Failed
- Verify AZURE_FUNCTION_KEY is set correctly
- Check backend URL is accessible
- Verify network connection
- Check Azure Function is running

### Messages Not Sending
- Check browser console for JavaScript errors (F12)
- Verify User ID is not empty
- Check debug logs for error details
- Verify backend endpoint is correct

## Notes
- This is a simplified version focusing on core functionality
- No task management or scheduling features
- Emphasis on debugging and statistics
- Minimal UI for maximum clarity
