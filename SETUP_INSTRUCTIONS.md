# Google Drive API Setup Instructions

## Prerequisites
1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Google Cloud Console Setup

### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### Step 2: Enable Google Drive API
1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Drive API"
3. Click on it and press "Enable"

### Step 3: Create Credentials

#### Option A: OAuth 2.0 (Recommended for personal use)
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop application" as the application type
4. Give it a name (e.g., "Finance Script")
5. Download the JSON file and save it as `credentials.json` in your project folder

#### Option B: Service Account (For automated/server use)
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the details and create
4. Go to the created service account and create a key (JSON format)
5. Download and save as `service-account.json` in your project folder
6. Share your Google Drive folders with the service account email

### Step 4: Configure OAuth Consent Screen (if using OAuth 2.0)
1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" for user type
3. Fill in the required information
4. Add your email to test users
5. Add the scope: `https://www.googleapis.com/auth/drive`

## Google Drive Folder Structure
Make sure your Google Drive has the following structure:
```
Bank/
├── HDFC/
│   └── 2024/
│       ├── BankstatementJan.xlsx
│       ├── BankstatementFeb.xlsx
│       └── ...
├── SBI/
│   └── 2024/
│       ├── BankstatementJan.xlsx
│       ├── BankstatementFeb.xlsx
│       └── ...
├── Finance.xlsx
└── merchant_category.json
```

## Configuration
1. Create a `config.json` file with your Google Drive folder IDs:
   ```json
   {
     "bank_folder_id": "your_bank_folder_id_here",
     "finance_file_id": "your_finance_xlsx_file_id_here"
   }
   ```

**Note:** The `merchant_category.json` file is automatically managed within the Bank folder. The script will:
- Search for it in the Bank folder
- Load existing merchant-category mappings if found
- Create a new file if it doesn't exist
- Update it automatically as you categorize transactions

To find folder/file IDs:
- Open the file/folder in Google Drive
- Look at the URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
- Copy the ID after `/folders/` or `/file/d/`

## Authentication Methods
The script supports both authentication methods:

1. **OAuth 2.0**: Place `credentials.json` in the project folder
2. **Service Account**: Place `service-account.json` in the project folder

OAuth 2.0 is recommended for personal use as it will open a browser for authentication.
Service Account is better for automated scripts but requires sharing folders with the service account email.
