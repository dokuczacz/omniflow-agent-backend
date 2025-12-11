#!/bin/bash
# Verification script to check if all new files are present

echo "================================================"
echo "  File Verification Script"
echo "================================================"
echo ""

# Check current branch
echo "1. Current branch:"
git branch --show-current
echo ""

# Check if up to date with remote
echo "2. Sync status:"
git status -sb
echo ""

# Check for new function directories
echo "3. New Azure Functions:"
if [ -d "save_interaction" ]; then
    echo "   ✓ save_interaction/ exists"
    ls -la save_interaction/
else
    echo "   ✗ save_interaction/ NOT FOUND"
fi
echo ""

if [ -d "get_interaction_history" ]; then
    echo "   ✓ get_interaction_history/ exists"
    ls -la get_interaction_history/
else
    echo "   ✗ get_interaction_history/ NOT FOUND"
fi
echo ""

# Check for documentation files
echo "4. New Documentation Files:"
for file in TESTING_PLAN.md DATA_EXTRACTION_IMPLEMENTATION.md IMPLEMENTATION_COMPLETE.md NEXT_STEPS.md QUICK_REFERENCE.md; do
    if [ -f "$file" ]; then
        echo "   ✓ $file exists ($(wc -l < "$file") lines)"
    else
        echo "   ✗ $file NOT FOUND"
    fi
done
echo ""

# Check VS Code configuration
echo "5. VS Code Configuration:"
if [ -f ".vscode/settings.json" ]; then
    echo "   ✓ .vscode/settings.json exists"
else
    echo "   ✗ .vscode/settings.json NOT FOUND"
fi

if [ -f ".vscode/README_NEW_FILES.md" ]; then
    echo "   ✓ .vscode/README_NEW_FILES.md exists"
else
    echo "   ✗ .vscode/README_NEW_FILES.md NOT FOUND"
fi
echo ""

# Check recent commits
echo "6. Recent commits on this branch:"
git log --oneline -6
echo ""

echo "================================================"
echo "  Verification Complete"
echo "================================================"
echo ""
echo "If files are missing, run:"
echo "  git fetch origin"
echo "  git pull origin copilot/implement-data-extraction-system"
