#!/bin/bash

# Script to package Teams app for deployment
# This creates a zip file with the app manifest and icons

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_PACKAGE_DIR="$SCRIPT_DIR/../appPackage"
OUTPUT_FILE="$SCRIPT_DIR/../lego-copilot-teams-app.zip"

echo "Packaging LEGO Copilot Teams App..."

# Check if appPackage directory exists
if [ ! -d "$APP_PACKAGE_DIR" ]; then
    echo "Error: appPackage directory not found"
    exit 1
fi

# Check required files
if [ ! -f "$APP_PACKAGE_DIR/manifest.json" ]; then
    echo "Error: manifest.json not found in appPackage"
    exit 1
fi

# Remove old package if exists
if [ -f "$OUTPUT_FILE" ]; then
    rm "$OUTPUT_FILE"
    echo "Removed old package"
fi

# Create zip package
cd "$APP_PACKAGE_DIR"
zip -r "$OUTPUT_FILE" * -x "*.DS_Store"
cd "$SCRIPT_DIR/.."

if [ -f "$OUTPUT_FILE" ]; then
    echo "✓ Teams app package created: lego-copilot-teams-app.zip"
    echo ""
    echo "Next steps:"
    echo "1. Open Microsoft Teams"
    echo "2. Go to Apps > Manage your apps > Upload an app"
    echo "3. Select 'Upload a custom app'"
    echo "4. Choose the lego-copilot-teams-app.zip file"
    echo ""
    echo "Note: Make sure to update BOT_ID and TEAMS_APP_ID in manifest.json before packaging"
else
    echo "Error: Failed to create package"
    exit 1
fi
