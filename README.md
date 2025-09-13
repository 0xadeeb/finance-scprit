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
- Excel file with professional formatting (current)
- (Planned) Optional CSV / JSON exporters will return later once stabilized

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
├── main.py                              # Entry script delegating to package
├── finance_analyzer/                    # Core application package
│   ├── main.py                          # FinanceAnalyzer orchestrator (async)
│   ├── constants.py                     # Shared constants & category lists
│   ├── models.py                        # Domain models (Transaction, etc.)
│   ├── transaction_processor.py         # Pure categorization & merchant mapping application
│   ├── config_manager.py                # Loads and validates config
│   ├── bank_parsers/                    # Bank-specific statement normalizers
│   │   ├── base.py
│   │   ├── hdfc.py
│   │   ├── sbi.py
│   │   └── registry.py                  # Bank parser registry
│   ├── statement_readers/               # Reads raw bank statement files
│   │   ├── base.py
│   │   ├── excel_reader.py
│   │   └── factory.py
│   ├── categorization_strategy/         # Strategy pattern for pending categorizations
│   │   ├── base.py
│   │   ├── user_prompt.py
│   │   └── auto.py
│   ├── interaction/                     # User interaction (CLI async port)
│   │   ├── port.py                      # Interaction port & DTOs
│   │   └── cli_async_port.py            # Concrete CLI implementation
│   ├── file_access/                     # Storage abstraction (local / future cloud)
│   │   ├── base.py
│   │   ├── local_accessor.py
│   │   ├── cloud_accessor.py
│   │   └── factory.py
│   ├── cloud_storage/                   # Cloud provider adapters
│   │   ├── base.py
│   │   ├── google_drive_api.py
│   │   ├── dropbox_api.py
│   │   ├── onedrive_api.py
│   │   └── factory.py
│   ├── services/
│   │   ├── merchant_mapping_store.py    # Dirty-tracked merchant mapping persistence
│   │   └── summary/                     # Summary domain + service (pandas isolated here)
│   │       ├── models.py                # SummaryData & SummaryRow domain
│   │       └── service.py               # SummaryService building SummaryData
│   ├── writers/                         # Output writers (domain-facing)
│   │   ├── base.py
│   │   ├── excel_writer.py              # Converts domain -> Excel (pandas internally)
│   │   └── factory.py
├── data/                                # (Example) Local data directory (not always committed)
├── config.json                          # Active configuration
├── config.json.template                 # Template configuration
├── config.local.example.json            # Example local configuration
├── requirements.txt                     # Python dependencies
├── README.md
├── SETUP_INSTRUCTIONS.md                # Cloud setup instructions
├── setup.sh                             # Optional setup script
├── credentials.json / token.json        # OAuth artifacts (should be gitignored in real setup)
└── LICENSE
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
