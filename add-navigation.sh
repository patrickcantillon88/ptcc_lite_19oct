#!/bin/bash

# Script to add navigation headers to all React apps
# This implements Phase 1 of the hybrid navigation approach

echo "🚀 Adding navigation headers to React apps..."

# List of apps to update (excluding those already done)
declare -A APPS=(
    ["mobile-pwa"]="📱:Mobile PWA:Quick student logging during lessons"
    ["project-guardian"]="🛡️:Digital Citizenship:Breach assessment and digital citizenship guidance" 
    ["classroom-tools"]="🛠️:Classroom Tools:Seating charts timers and classroom utilities"
    ["behaviour-management"]="📊:Behaviour Management:Live lesson tracking and behavior strikes"
    ["progress-dashboard"]="📈:Progress Dashboard:Visual analytics for class and student progress"
    ["seating-chart"]="🪑:Seating Chart:Optimal seating arrangements based on behavior data"
    ["group-formation"]="👥:Group Formation:Create optimal student groups for learning"
    ["differentiation"]="🎯:Differentiation:Performance analysis for differentiated instruction"
    ["quiz-upload"]="📤:Quiz Upload:Upload and process quiz results from CSV files"
    ["performance-trends"]="📈:Performance Trends:Student performance tracking over time"
    ["progress-levels"]="📊:Progress Levels:Grade-level expectations analysis"
    ["at-risk-students"]="⚠️:At-Risk Students:Identify students needing intervention"
    ["assessment-analytics-overview"]="📊:Assessment Overview:Assessment analytics dashboard and tools"
)

for app_dir in "${!APPS[@]}"; do
    IFS=':' read -r icon name description <<< "${APPS[$app_dir]}"
    
    echo "📝 Processing $app_dir ($name)..."
    
    app_path="frontend/$app_dir"
    
    # Skip if directory doesn't exist
    if [ ! -d "$app_path" ]; then
        echo "⚠️  Directory $app_path not found, skipping..."
        continue
    fi
    
    # Find the main App file (.jsx, .tsx, .js, .ts)
    app_file=""
    for ext in "tsx" "jsx" "ts" "js"; do
        if [ -f "$app_path/src/App.$ext" ]; then
            app_file="$app_path/src/App.$ext"
            break
        fi
    done
    
    if [ -z "$app_file" ]; then
        echo "⚠️  No App file found in $app_path/src/, skipping..."
        continue
    fi
    
    echo "  📄 Found: $app_file"
    
    # Create backup
    cp "$app_file" "$app_file.backup"
    
    # Check if already has AppNavigation import
    if grep -q "AppNavigation" "$app_file"; then
        echo "  ✅ Already has navigation, skipping..."
        continue
    fi
    
    # Add import statements at the top (after existing imports)
    if [[ "$app_file" == *.tsx ]] || [[ "$app_file" == *.ts ]]; then
        # TypeScript file
        sed -i.tmp '1a\
import AppNavigation from '"'"'../../shared/AppNavigation.tsx'"'"'\
import '"'"'../../shared/AppNavigation.css'"'"'
' "$app_file"
    else
        # JavaScript file
        sed -i.tmp '1a\
import AppNavigation from '"'"'../../shared/AppNavigation.tsx'"'"'\
import '"'"'../../shared/AppNavigation.css'"'"'
' "$app_file"
    fi
    
    # Add navigation component after opening div or first element
    # This is a simple approach - may need manual adjustment for some apps
    sed -i.tmp 's|<div className={`app|<div className={`app|' "$app_file"
    sed -i.tmp '/className={`app/a\
        {/* Navigation Header */}\
        <AppNavigation \
          appName="'"$name"'"\
          appIcon="'"$icon"'"\
          appDescription="'"$description"'"\
        />
' "$app_file"
    
    # Clean up temp file
    rm "$app_file.tmp"
    
    echo "  ✅ Added navigation to $name"
done

echo ""
echo "🎉 Navigation update complete!"
echo ""
echo "📋 Summary:"
echo "  • Added consistent navigation headers to all React apps"
echo "  • Each app now has a 'Back to Dashboard' button"
echo "  • All apps are linked in a collapsible navigation menu"
echo "  • Backup files created with .backup extension"
echo ""
echo "🔄 Next steps:"
echo "  • Test each app to ensure navigation works"
echo "  • Restart development servers if needed"
echo "  • Fine-tune styling if required"
echo ""
echo "💡 To test: Visit any app and click '← Dashboard' to return"