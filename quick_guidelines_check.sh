#!/bin/bash
# Quick Guidelines Adherence Check
# Run this before any major development task

echo "🔍 QUICK GUIDELINES ADHERENCE CHECK"
echo "=================================="

# Check if PROJECT_GUIDELINES.md exists and show its size
if [ -f "PROJECT_GUIDELINES.md" ]; then
    SIZE=$(wc -c < PROJECT_GUIDELINES.md)
    LINES=$(wc -l < PROJECT_GUIDELINES.md)
    echo "✅ PROJECT_GUIDELINES.md: ${SIZE} bytes, ${LINES} lines"
else
    echo "❌ PROJECT_GUIDELINES.md NOT FOUND!"
    exit 1
fi

# Quick file structure check
echo ""
echo "📁 Key File Structure:"
[ -f "app.py" ] && echo "✅ app.py" || echo "❌ app.py missing"
[ -f "ttrpg-config.json" ] && echo "✅ ttrpg-config.json" || echo "❌ ttrpg-config.json missing"
[ -f "requirements.txt" ] && echo "✅ requirements.txt" || echo "❌ requirements.txt missing"

# Check for old guidelines files that should be removed
echo ""
echo "🗑️  Old Guidelines Check:"
OLD_FILES=("DEVELOPER_QUICK_REFERENCE.md" "ENHANCED_FORMATTING_GUIDE.md" "FORMATTING_IMPLEMENTATION_SUMMARY.md" "INTERFACE_UPDATES.md" "LAYOUT_FIX_SUMMARY.md")

FOUND_OLD=false
for file in "${OLD_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "⚠️  Old file found: $file (should be deleted)"
        FOUND_OLD=true
    fi
done

if [ "$FOUND_OLD" = false ]; then
    echo "✅ No old guidelines files found"
fi

echo ""
echo "📋 REMEMBER: Always consult PROJECT_GUIDELINES.md before making changes!"
echo "🔗 Location: /workspaces/mydemerzel-project/PROJECT_GUIDELINES.md"
echo ""
echo "✅ Quick check complete. Proceed with guidelines in mind."
