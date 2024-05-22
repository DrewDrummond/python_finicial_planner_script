"""This will keep track of the user's checking account transactions and categorize them based on keywords in the description."""

import pandas as pd
import re

class CheckingTracker:
    def __init__(self, file_path):
        self.file_path = file_path  # Path to the CSV file containing the transaction data
        self.df = None  # DataFrame to store the transaction data
        # Dictionary to categorize transactions based on keywords in the description
        self.categories = {
            'reoccurring': [
                r'reoccuring', r'microsoft', r'apple', 
            ],
            'target': [
                r'target'
            ],
            'transfers': [
                r'transfer',
            ], 
            'income': [
                r'zelle from', 
            ],
            'payments': [
                r'zelle', r'purchase auth'
            ]
        }

    def load_csv(self):
        # Try to load the CSV file into a DataFrame
        try:
            self.df = pd.read_csv(self.file_path, header=None, names=['Date', 'Amount', 'Symbol', 'Symbol2', 'Description'])
            print("CSV file loaded successfully.")
        except Exception as e:
            # If there's an error, print it
            print(f"Error loading CSV file: {e}")

    def clean_data(self):
        # Keep only relevant columns
        self.df = self.df[['Date', 'Amount', 'Description']]
        # Remove any non-numeric characters from the Amount column and convert to numeric
        self.df['Amount'] = self.df['Amount'].replace('[^\d.-]', '', regex=True)  # Use regex to remove unwanted characters
        self.df['Amount'] = self.df['Amount'].replace('', pd.NA)  # Replace empty strings with NaN
        self.df['Amount'] = pd.to_numeric(self.df['Amount'], errors='coerce')  # Convert to numeric, setting invalid parsing as NaN

    def categorize_transaction(self, description):
        description = description.lower()  # Convert description to lowercase for case-insensitive matching
        category_scores = {category: 0 for category in self.categories}  # Initialize scores for each category

        for category, keywords in self.categories.items():
            for keyword in keywords:
                if re.search(keyword, description, re.IGNORECASE):  # Use regex to search for the keyword in the description
                    category_scores[category] += 1  # Increment the score for the matched category

        # Determine the category with the highest score
        best_category = max(category_scores, key=category_scores.get)
        return best_category if category_scores[best_category] > 0 else 'other'  # Return 'other' if no category has a positive score

    def apply_categorization(self):
        # Apply categorization to each transaction based on the description
        self.df['Category'] = self.df['Description'].apply(lambda x: self.categorize_transaction(x))  # Use apply to run categorize_transaction on each description

    def process_dates(self):
        # Convert the date column to datetime format
        self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')  # Convert to datetime, coercing errors to NaT
        # Drop any rows with invalid dates
        self.df = self.df.dropna(subset=['Date'])  # Drop rows where 'Date' is NaT

    def sort_data(self):
        # Sort the DataFrame by date and category
        self.df = self.df.sort_values(by=['Date', 'Category'])  # Sort by date and then by category

    def display_monthly_totals(self, grouped):
        # Calculate and return the total spent for each month
        monthly_totals = []
        for name, group in grouped:
            expenses = group[group['Amount'] < 0]  # Consider only expenses (negative amounts)
            total_spent = expenses['Amount'].sum()  # Sum the amounts
            monthly_totals.append(f"Total spent in {name}: ${total_spent:.2f}")  # Append the formatted total
        return monthly_totals

    def display_data(self):
        # Set display options for better readability
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)

        # Check if the date column is in datetime format
        if self.df['Date'].dtype == '<M8[ns]':  # '<M8[ns]' indicates datetime64[ns] dtype
            self.df['YearMonth'] = self.df['Date'].dt.to_period('M')  # Extract YearMonth period from date
            grouped = self.df.groupby('YearMonth')  # Group the DataFrame by YearMonth

            # Print transactions for each month
            for name, group in grouped:
                print(f"\nTransactions for {name}:\n")
                print(group[['Date', 'Amount', 'Description', 'Category']])

            # Print monthly category totals and percentages
            self.display_monthly_category_totals(grouped)

        else:
            print("Date conversion failed; check data format.")

    def display_monthly_category_totals(self, grouped):
        for name, group in grouped:
            total_spent = group['Amount'][group['Amount'] < 0].sum()  # Calculate total spent for the month
            print(f"\nTotal spent in {name}: ${total_spent:.2f}")  # Print total spent for the month

            category_totals = group[group['Amount'] < 0].groupby('Category')['Amount'].sum()  # Calculate total spent per category for the month

            # Calculate percentage spent per category for the month
            category_percentages = (category_totals / total_spent) * 100

            # Combine totals and percentages into a DataFrame for sorting
            category_stats = pd.DataFrame({
                'Total': category_totals,
                'Percentage': category_percentages
            })

            # Sort the categories by percentage in descending order
            category_stats = category_stats.sort_values(by='Percentage', ascending=False)

            # Print the totals and percentages for each category for the month
            for category, stats in category_stats.iterrows():
                total = stats['Total']
                percentage = stats['Percentage']
                print(f"    - {category}: ${abs(total):.2f} ({percentage:.2f}%)")  # Indent for better readability

    def run(self):
        # Run all the methods in sequence to process and display the data
        self.load_csv()  # Load the data from the CSV file
        self.clean_data()  # Clean the data to ensure it's in the right format
        self.apply_categorization()  # Categorize each transaction
        self.process_dates()  # Convert and validate the date format
        self.sort_data()  # Sort the data by date and category
        self.display_data()  # Display the processed data and monthly totals


# Instantiate and run the CheckingTracker
checking_csv_file_path = "/Users/drewdrummond/Documents/coding projects/Python_expense_tracker/CSV's/checking.csv"
tracker = CheckingTracker(checking_csv_file_path)
tracker.run()
