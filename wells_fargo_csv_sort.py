# Importing my libraries
import pandas as pd
import re

# Path to the CSV file saved as a variable
file_path = "/Users/drewdrummond/Documents/coding projects/Python_expense_tracker/CSV's/new_credit.csv"

# Reading the CSV file
df = pd.read_csv(file_path, header=None, names=['Date', 'Amount', 'Symbol', 'symbol', 'Description'])

# Keeping only the relevant columns: Date, Amount, Description
df = df[['Date', 'Amount', 'Description']]

# Clean the Amount column and replace non-numeric characters, handling errors
df['Amount'] = df['Amount'].replace('[^\d.-]', '', regex=True)

# Replace empty strings with NaN
df['Amount'] = df['Amount'].replace('', pd.NA)

# Convert Amount column to numeric, handling errors
df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

# Categories for the df descriptions
categories = {
    'food': [r'MCDONALD\S*', r'TACO BELL', r'CHICK-FIL-A', r'OLIVE GARDEN', 
            r'7-ELEVEN', r'CHIPOTLE', r'CULVER\'S', r'CHINA TASTE', r'SARASOTA BOBA TEA',
            r'DAIRY QUEEN', r'TST\* THE MELTING POT', r'FIRST WATCH', r'TARGET\.COM'],
    'material': [],
    'entertainment': [r'HI TEC PAINTBALL PARK', r'K1 SPEED TAMPA', r'THE MELTING POT', 
                    r'PAR\'SMOOTHIE KING', r'RACETRAC', r'K1 SPEED'],
    'reoccuring': [r'ONLINE PAYMENT THANK YOU', r'GITHUB INC', r'AMZN Mktp US', 
                    r'PHOTOENFORCEMENT PROGRAM'],
    'other': [r'BIG DANS CAR WASH', r'EXXON', r'CHEGG ORDER', r'ROYAL TEA', r'PUBLIX']
}

# A function to sort the df descriptions into its categories
def categorize_transaction(description, categories):
    for category, keywords in categories.items():
        for keyword in keywords:
            if re.search(keyword, description, re.IGNORECASE):
                return category
    return 'other'

# Apply the categorization function to the 'Description' column
df['Category'] = df['Description'].apply(lambda x: categorize_transaction(x, categories))

# Try converting the 'Date' column with more flexibility
df['Date'] = pd.to_datetime(df['Date'], errors='coerce', infer_datetime_format=True)

# Drop rows where 'Date' conversion resulted in NaT (Not a Time)
df = df.dropna(subset=['Date'])

# Extract only the date part and the month part
df['Date'] = df['Date'].dt.date

# Sort by month first and then by category
sorted_df = df.sort_values(by=['Date', 'Category'])


# Setting display options to show the entire DataFrame
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', None)  # Adjust the width to avoid line breaks
pd.set_option('display.max_colwidth', None)  # Show full column content

# Print the entire DataFrame
print(sorted_df)
