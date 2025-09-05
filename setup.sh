#!/bin/bash

echo "🚀 Setting up Finance Script with Google Drive API"
echo "=================================================="

# Install required packages
echo "📦 Installing required Python packages..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Packages installed successfully"
else
    echo "❌ Failed to install packages"
    exit 1
fi

# Check if config file exists
if [ ! -f "config.json" ]; then
    echo "📝 Creating config.json from template..."
    cp config.json.template config.json
    echo "⚠️  Please edit config.json with your Google Drive file/folder IDs"
    echo "   See SETUP_INSTRUCTIONS.md for details on how to get these IDs"
else
    echo "✅ config.json already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Follow SETUP_INSTRUCTIONS.md to set up Google Drive API"
echo "2. Edit config.json with your Google Drive file/folder IDs"
echo "3. Add your credentials file (credentials.json or service-account.json)"
echo "4. Run: python main_gdrive.py"
echo ""
echo "📚 For detailed instructions, see SETUP_INSTRUCTIONS.md"
