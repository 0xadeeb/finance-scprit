# Finance Analyzer

A Python application that analyzes bank statements and generates financial summaries. Supports both local file processing and cloud storage integration.

## Features

- 📊 **Multi-Bank Support** - HDFC, SBI, and extensible for other banks
- 🏠 **Local & Cloud Storage** - Work with local files or Google Drive
- � **Smart Transaction Parsing** - Automatic merchant categorization
- 📈 **Excel Reports** - Professional formatted output with charts
- 🧪 **Comprehensive Testing** - Full test suite included

## Setup and Installation

### Prerequisites
- Python 3.7+
- pip package manager

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd finance-scprit
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Local File Processing (Recommended for beginners)

1. **Create configuration file:**
   ```bash
   cp config.local.example.json config.json
   ```

2. **Organize your files:**
   ```
   data/
   ├── Finance.xlsx                    # Main finance spreadsheet
   └── banks/                          # Bank statements folder
       ├── HDFC/2024/
       │   ├── BankstatementJan.xlsx
       │   └── BankstatementFeb.xlsx
       └── SBI/2024/
           └── BankstatementJan.xlsx
   ```

3. **Update config.json:**
   ```json
   {
     "storage_type": "local",
     "local_base_path": "./data",
     "bank_folder_id": "banks",
     "finance_file_id": "Finance.xlsx"
   }
   ```

### Cloud Storage (Google Drive)

1. **Set up Google Drive API:**
   - Follow detailed instructions in `SETUP_INSTRUCTIONS.md`
   - Create credentials in Google Cloud Console
   - Download credentials JSON file

2. **Create cloud configuration:**
   ```json
   {
     "storage_type": "cloud",
     "cloud_provider": "google_drive",
     "bank_folder_id": "your_google_drive_folder_id",
     "finance_file_id": "your_finance_xlsx_file_id"
   }
   ```

## Running the Application

### Basic Usage
```bash
python main.py
```

### Running Tests
```bash
# Run all tests
python tests/run_tests.py

# Run specific test
python tests/test_hdfc_parsing.py
```

## Supported Banks

- **HDFC Bank** - Full support with UPI transaction parsing
- **State Bank of India (SBI)** - Complete transaction analysis
- **Extensible** - Easy to add support for other banks

## File Formats

### Input
- Excel files (.xlsx, .xls)
- CSV files (with proper bank statement format)

### Output  
- Excel files with professional formatting
- CSV files for data analysis
- JSON files for integration

## Troubleshooting

### Common Issues

**File not found errors:**
- Check file paths in `config.json`
- Ensure files exist and are accessible
- Verify folder structure matches configuration

**Permission errors:**
- Close Excel files before running
- Check file/folder permissions
- Run terminal as administrator if needed (Windows)

**Import errors:**
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (3.7+ required)

**Cloud storage issues:**
- Verify Google Drive API setup in `SETUP_INSTRUCTIONS.md`
- Check credential files and permissions
- Ensure file IDs in config are correct

### Getting Help

For detailed setup instructions and troubleshooting:
- See `SETUP_INSTRUCTIONS.md` for Google Drive API setup
- Check test files in `/tests/` for usage examples
- Review configuration templates in project root

## Development

### Project Structure
```
finance-scprit/
├── main.py                     # Entry point
├── finance_analyzer/           # Main package
│   ├── bank_parsers/          # Bank-specific parsing
│   ├── cloud_storage/         # Cloud storage providers  
│   └── file_access/           # File system abstraction
├── tests/                     # Test suite
├── config.json               # Configuration
└── requirements.txt          # Dependencies
```

### Adding New Banks
1. Create parser in `finance_analyzer/bank_parsers/`
2. Extend from `Bank` base class
3. Implement `parse_transaction()` method
4. Register in `bank_parsers/registry.py`

### Contributing
- All code changes should include tests
- Run full test suite before submitting
- Follow existing code patterns and structure
