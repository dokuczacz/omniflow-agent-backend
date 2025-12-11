# OmniFlow Assistant - Simplified UI

## Overview

This is a simplified Streamlit-based user interface for the OmniFlow Assistant backend. The UI focuses on core functionality: chat interaction with debugging and statistics capabilities.

## Features

### ✅ What's Included

1. **Simple Chat Interface**
   - Clean, scrollable chat display
   - User and assistant messages clearly distinguished
   - Real-time message streaming

2. **Debugging Tools** (Above Chat)
   - Backend connection status indicator
   - Average response time metric
   - Message counter
   - Last error display
   - Expandable debug panel with:
     - Response time tracking (last 5 calls)
     - Debug logs (last 10 entries with color coding)
     - System information display

3. **Minimal Configuration** (Sidebar)
   - User ID input
   - Category selector
   - No complex features or settings

### ❌ What's Removed

The following features were intentionally removed to simplify the UI:
- Task management ("Add Task", "View Tasks" buttons)
- Schedule/agenda views
- File management interfaces
- Complex multi-column layouts
- Unnecessary widgets and controls

## Architecture

### Frontend (streamlit_simple.py)
- **Configuration**: Backend URL, authentication
- **Session State**: Messages, debug logs, response times
- **UI Components**: 
  - Debug toolbar (4 metrics)
  - Expandable debug panel (3 tabs)
  - Chat interface
  - Minimal sidebar

### Backend Integration
The UI communicates with Azure Functions backend:
- **Endpoint**: `tool_call_handler`
- **Authentication**: X-User-Id header + Function Key
- **Payload**: message, user_id, thread_id

## Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Environment Variables
```bash
export AZURE_FUNCTION_KEY="your_function_key_here"
```

### Run
```bash
streamlit run streamlit_simple.py
```

The UI will open at `http://localhost:8501`

## Usage

### Basic Chat
1. Set your User ID in the sidebar (or use default)
2. Select a category
3. Type a message in the chat input
4. Press Enter to send
5. Wait for assistant response

### View Debug Information
1. Click "🔍 Debug Panel" to expand
2. Switch between tabs:
   - **Response Times**: See API call performance
   - **Debug Logs**: View system events and errors
   - **System Info**: Check configuration details

### Monitor System Health
- **Backend Status**: Shows connection state (✅ Connected / ❌ Error)
- **Avg Response**: Average API response time in seconds
- **Messages**: Total message count in current session
- **Last Error**: Most recent error message (if any)

## Debugging Features

### Response Time Tracking
Every backend API call is tracked with:
- Endpoint name
- Response time (seconds)
- Timestamp

The last 5 calls are retained and displayed in the debug panel.

### Debug Logging
System events are logged with severity levels:
- 🔵 **INFO**: General information
- 🟢 **SUCCESS**: Successful operations
- 🔴 **ERROR**: Failures and exceptions
- 🟡 **WARNING**: Warnings (if needed)

The last 10 logs are retained and displayed in reverse chronological order.

### Error Display
Errors are surfaced in multiple places:
1. Backend status metric (top of page)
2. Last Error metric (red error box)
3. Debug logs (with full details)
4. Chat response (user-facing error message)

## Design Principles

1. **Simplicity First**: Only essential features included
2. **Debugging Focus**: Extensive monitoring and logging
3. **Clear Visual Hierarchy**: Important info at the top
4. **Minimal Configuration**: Just User ID and Category
5. **Error Transparency**: All errors clearly displayed

## File Structure

```
omniflow-agent-backend/
├── streamlit_simple.py           # Main UI application
├── requirements.txt              # Python dependencies (includes streamlit)
├── UI_README.md                  # This file
└── UI_TESTING_INSTRUCTIONS.md   # Comprehensive testing guide
```

## Backend Configuration

The UI is configured to connect to:
- **Backend URL**: `https://agentbackendservice-dfcpcudzeah4b6ae.northeurope-01.azurewebsites.net/api`
- **Endpoint**: `tool_call_handler`
- **Authentication**: Function Key (from environment variable)

To use a different backend, modify the `BACKEND_URL` constant in `streamlit_simple.py`.

## Troubleshooting

### UI Won't Start
- Check Python version (3.8+ required)
- Install streamlit: `pip install streamlit`
- Check port 8501 is available

### Backend Connection Issues
- Verify `AZURE_FUNCTION_KEY` environment variable is set
- Check backend URL is accessible
- Look at debug logs for specific error messages

### Messages Not Sending
- Check User ID is not empty
- Verify category is selected
- Open browser console (F12) for JavaScript errors
- Check debug panel for error details

### Slow Response Times
- Normal response time: 1-3 seconds
- Check backend status metric
- Review response times in debug panel
- Verify network connection

## Testing

See `UI_TESTING_INSTRUCTIONS.md` for comprehensive testing procedures covering:
- Initial load
- Configuration
- Debug panel functionality
- Chat interface
- Error handling
- Response time tracking
- Multiple test scenarios

## Comparison: Simple vs. Complex UI

### Removed from Previous Version
- ❌ Task management buttons
- ❌ File management interface
- ❌ "View Schedule" features
- ❌ Complex multi-column layouts
- ❌ Today's tasks section
- ❌ Quick actions

### Added/Enhanced
- ✅ Response time tracking
- ✅ Debug logging system
- ✅ System status indicators
- ✅ Error transparency
- ✅ Simplified layout
- ✅ Focus on core chat functionality

## Version History

### v1.0 - Simplified Version (Current)
- Simple chat interface
- Debugging and statistics focus
- Removed task/schedule management
- Enhanced error tracking
- Response time monitoring

## Support

For issues or questions:
1. Check `UI_TESTING_INSTRUCTIONS.md`
2. Review debug logs in the UI
3. Check backend logs in Azure
4. Verify environment configuration

## Future Enhancements (To Be Confirmed)

Potential additions based on user needs:
- Additional debug metrics
- Export debug logs
- Performance graphs
- More detailed system information
- Custom backend URL input
