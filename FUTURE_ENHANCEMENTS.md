# Future Enhancements - OmniFlow Backend

## 📋 Batch Operations & Smart Functions (Phase 4)

### Status: PLANNED - Do Later (Post-MVP)

---

## **Smart GET Functions** (Priority: HIGH - Next Phase)

### Tier 1: Implement Soon (1.5 hours)
- [ ] `get_file_stats` - File metadata without loading content
  - Returns: entry_count, size, last_modified, categories
  - Use: Sidebar stat badges, fast UI updates
  
- [ ] `get_due_today` - Entries due today across all files
  - Returns: All entries from all files with today's date
  - Use: Right-pane "Today" widget, daily agenda
  
- [ ] `get_recent_entries` - Last N entries from file
  - Returns: Most recent entries (limit: 5-20)
  - Use: "Recent" tabs, latest notes/tasks view

### Tier 2: Nice to Have (2-3 hours)
- [ ] `get_date_range` - Entries between dates
  - Use: Calendar views, week/month planning
  
- [ ] `get_summary_stats` - Overview all categories
  - Use: Dashboard, at-a-glance metrics
  
- [ ] `get_search` - Full-text search
  - Use: Find tasks/notes by keyword

---

## **Batch Operations** (Priority: MEDIUM - Phase 5)

### Rationale
Better than batch_download because:
- Reduce API calls (1 call instead of 10)
- Save bandwidth (sending vs downloading)
- Atomic transactions (all succeed or all fail)
- Perfect for bulk task management

### To Implement
- [ ] `batch_add_entries` - Add multiple entries across files
  - Use: Bulk import, quick add 10 tasks
  
- [ ] `batch_update_entries` - Update multiple entries
  - Use: Mark all tasks done, bulk status changes
  
- [ ] `batch_archive` - Move/archive multiple files
  - Use: Seasonal cleanup, archive old notes

---

## **Batch Download** (Priority: LOW - Phase 6+)

### Status: SKIP for now
- Not needed for real-time Streamlit UI
- Smart GET functions are faster + lighter
- Only useful for manual export/backup

### When to Add
- If "Export all as ZIP" feature requested
- For one-time migrations
- Manual archival use cases

---

## Decision Log
- **Date**: 2025-12-09
- **Decision**: Focus on Smart GET functions first
- **Rationale**: Better UX, faster responses, perfect for Streamlit dashboard
- **Batch Download**: Defer indefinitely (can add anytime as bonus feature)
