"""
Constants used throughout the finance analyzer.
"""

import os

# Directories
TEMP_DIR = './temp'
LOCAL_MERCHANT_CATEGORY_FILE = os.path.join(TEMP_DIR, 'merchant_category.json')
LOCAL_OUTPUT_FILE = os.path.join(TEMP_DIR, 'Finance.xlsx')

# Categories
CREDIT_CATEGORIES = [
    "Salary",
]

DEBIT_CATEGORIES = [
    "Food",
    "House",                    # House rent, furnishing etc
    "Entertainment",
    "Clothes & Accessories",    # Cloths and accessories
    "Transportation",           # Cabs, petrol, cleaning vehicles etc
    "Health",                   # Doctor, Medicines etc
    "Fitness",                 # Gym, football, boxing etc
    "Grooming",
    "Grocery",                  # Household items - Utensils, cleaning products etc
    "Network",
    "Free",                     # Give money for free to friends or kins
    "Misl"                      # General category or don't know the category
]

NET_CATEGORIES = [
    "Investment",
    "Deposit",
    "Lend",
    "Borrow"
] # Non Expenditure categories - not being used now

CATEGORIES = CREDIT_CATEGORIES + DEBIT_CATEGORIES + NET_CATEGORIES

BALANCE_ROWS = ['Opening Bank Bal.', 'Opening In Hand', 'Closing In Hand', 'Closing Bank Bal.']

# Category mappings
CAT_MAPPING = {
    "cloths": "Clothes & Accessories",
    "accessories": "Clothes & Accessories",
    "petrol": "Transportation",
    "travel": "Transportation",
    "transport": "Transportation",
    "cab": "Transportation",
    "utilities": "Grocery",
    "doctor": "Health",
    "rent": "House",
    "medicine": "Health",
    "other": "Misl"
}

# Bank accounts
BANK_ACCOUNTS = ["SBI", "HDFC"]
