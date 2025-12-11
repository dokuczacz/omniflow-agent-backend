# Troubleshooting: Can't Open Files in VS Code

## Quick Diagnosis

Run this command in your terminal to check file status:
```bash
./verify_files.sh
```

Or manually check:
```bash
git status
git log --oneline -6
ls -la save_interaction/ get_interaction_history/
```

---

## Common Issues & Solutions

### Issue 1: Files Not Synced from GitHub

**Symptoms**: Files don't appear in VS Code Explorer

**Solution**:
```bash
# 1. Fetch latest changes
git fetch origin

# 2. Make sure you're on the right branch
git checkout copilot/implement-data-extraction-system

# 3. Pull the changes (this is the most important step!)
git pull origin copilot/implement-data-extraction-system

# 4. Verify files exist
ls -la save_interaction/ get_interaction_history/
```

### Issue 2: VS Code Not Showing Files

**Symptoms**: Git shows files but VS Code doesn't display them

**Solutions**:

**A. Refresh VS Code Explorer**
- Click the refresh icon in the Explorer pane (top right of file tree)

**B. Reload VS Code Window**
- Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
- Type "Reload Window"
- Press Enter

**C. Close and Reopen Folder**
- File → Close Folder
- File → Open Folder → Select your project folder

### Issue 3: Git Says "Already Up to Date" But Files Missing

**Solution**:
```bash
# Force reset to remote state (WARNING: loses local uncommitted changes)
git fetch origin
git reset --hard origin/copilot/implement-data-extraction-system

# Verify files are now present
ls -la save_interaction/
```

### Issue 4: Permission Issues

**Symptoms**: Can't open or edit files

**Solution**:
```bash
# Check file permissions
ls -la save_interaction/__init__.py

# Fix permissions if needed (on Linux/Mac)
chmod 644 save_interaction/__init__.py
chmod 644 get_interaction_history/__init__.py
```

### Issue 5: Files Open But Are Empty or Corrupted

**Solution**:
```bash
# Check file contents
cat save_interaction/__init__.py | head -20

# Check file size
ls -lh save_interaction/__init__.py

# If file is corrupted, re-pull
git checkout origin/copilot/implement-data-extraction-system -- save_interaction/__init__.py
```

---

## Expected Files After Sync

You should see these new files/folders:

### New Folders
- 📁 `save_interaction/`
  - `__init__.py` (131 lines)
  - `function.json`
- 📁 `get_interaction_history/`
  - `__init__.py` (138 lines)
  - `function.json`

### New Documentation (in root folder)
- 📄 `TESTING_PLAN.md` (546 lines)
- 📄 `DATA_EXTRACTION_IMPLEMENTATION.md` (444 lines)
- 📄 `IMPLEMENTATION_COMPLETE.md` (371 lines)
- 📄 `NEXT_STEPS.md` (372 lines)
- 📄 `QUICK_REFERENCE.md` (203 lines)

### VS Code Configuration
- 📁 `.vscode/`
  - `settings.json`
  - `README_NEW_FILES.md`

---

## Step-by-Step Sync Process

If nothing works, try this complete reset:

```bash
# 1. Save any local work (if you have uncommitted changes)
git stash

# 2. Fetch all remote changes
git fetch origin

# 3. Switch to the branch
git checkout copilot/implement-data-extraction-system

# 4. Reset to match remote exactly
git reset --hard origin/copilot/implement-data-extraction-system

# 5. Verify files exist
./verify_files.sh

# 6. Open in VS Code
# Close and reopen VS Code, or reload window
```

---

## Verify Everything Works

Run these commands to confirm:

```bash
# Check file count
find . -name "*.py" -path "./save_interaction/*" -o -path "./get_interaction_history/*" | wc -l
# Should show: 2

# Check line count in key files
wc -l save_interaction/__init__.py get_interaction_history/__init__.py
# Should show: 131 and 138

# Check git tracking
git ls-files | grep -E "(save_interaction|get_interaction_history)" | wc -l
# Should show: 4
```

---

## Still Having Issues?

1. **Check your Git version**: `git --version` (should be 2.x or higher)
2. **Check disk space**: `df -h .` (need at least a few MB free)
3. **Check network**: Can you access GitHub? `ping github.com`
4. **Try cloning fresh**: In a new directory:
   ```bash
   git clone https://github.com/dokuczacz/omniflow-agent-backend.git fresh-clone
   cd fresh-clone
   git checkout copilot/implement-data-extraction-system
   ```

---

## VS Code Specific Issues

### Issue: "Source Control" shows changes but files won't open

**Solution**:
1. Open VS Code Settings (Ctrl+,)
2. Search for "git.enabled"
3. Make sure it's checked
4. Search for "files.exclude"
5. Make sure `save_interaction` and `get_interaction_history` are NOT in the exclude list

### Issue: Files in "Untracked" or "Changes"

This is normal if you haven't pulled yet. Just run:
```bash
git pull origin copilot/implement-data-extraction-system
```

---

## Quick Reference Commands

```bash
# See what branch you're on
git branch --show-current

# See if you're behind remote
git status -sb

# Pull latest changes
git pull origin copilot/implement-data-extraction-system

# Force update to remote state
git reset --hard origin/copilot/implement-data-extraction-system

# List all tracked files
git ls-files

# See what changed in last 6 commits
git log --oneline -6 --stat
```

---

## Contact Points

If you've tried everything and still can't open files:
1. Check the commit hash: Should be `f32833e` or later
2. Verify you're on branch: `copilot/implement-data-extraction-system`
3. Run: `git log --oneline -1` to see your current commit
