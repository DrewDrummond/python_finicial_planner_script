import pandas as pd
import re

class SavingsTracker:
    def __init__(self, file_path):
        self.file_path = file_path  # Path to the CSV file containing the savings data
        self.df = None  # DataFrame to store the savings data
        # Dictionary to categorize transactions based on keywords in the description
        self.categories = {
        'income': [
                r'TARGET CORPORATI PAYROLL', 
                r'eDeposit in Branch',
                r'INTEREST PAYMENT', r'ONLINE TRANSFER FROM DRUMMOND D', r'interest'
            ],
            'payments': [
                r'FID BKG SVC LLC MONEYLINE',
                r'WF Credit Card AUTO PAY', 
                r'CRUNCH CLUB FEES',
                r'ONLINE TRANSFER REF #IB',
                r'ZELLE TO',
                r'PRIZEPICKS INTERNET',
                r'ONLINE TRANSFER TO DRUMMOND D'
            ],
            'ignore': [
                r'ONLINE TRANSFER TO DRUMMOND D',   
            ],
}

    def load_csv(self):
        # Try to load the CSV file into a DataFrame
        try:
            self.df = pd.read_csv(self.file_path, header=None, names=['Date y/m/d', 'Amount', 'Symbol', 'Symbol2', 'Description'])
            print("CSV file loaded successfully.")
        except Exception as e:
            # If there's an error, print it
            print(f"Error loading CSV file: {e}")


    def clean_data(self):
        # Keep only relevant columns
        self.df = self.df[['Date y/m/d', 'Amount', 'Description']]
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
        self.df['Date y/m/d'] = pd.to_datetime(self.df['Date y/m/d'], errors='coerce')  # Convert to datetime, coercing errors to NaT
        # Drop any rows with invalid dates
        self.df = self.df.dropna(subset=['Date y/m/d'])  # Drop rows where 'Date y/m/d' is NaT
        # Verify the conversion
        print("\nDate conversion complete. Data types:\n", self.df.dtypes)


    def sort_data(self):
        # Sort the DataFrame by date and category
        self.df = self.df.sort_values(by=['Date y/m/d', 'Category'])  # Sort by date and then by category
    
    
    def display_data(self):
        # Set display options for better readability
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
    
    def display_monthly_category_totals(self):
        self.df['YearMonth'] = self.df['Date y/m/d'].dt.to_period('M')  # Extract YearMonth period from date
        grouped = self.df.groupby('YearMonth')  # Group the DataFrame by YearMonth

        for name, group in grouped:
            total_spent = group['Amount'].sum()  # Calculate total for the month
            print(f"\nTotal in {name}: ${total_spent:.2f}")  # Print total for the month
            
            category_totals = group.groupby('Category')['Amount'].sum()  # Calculate total per category for the month
            # Calculate percentage per category for the month
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
                print(f"    - {category}: ${abs(total):.2f}, = {percentage:.2f}%")  # Indent for better readability

    def run(self):
        """
        Run all methods to process and display the savings data.
        """
        self.load_csv()  # Load the CSV file
        self.clean_data()  # Clean the data
        self.apply_categorization()  # Categorize the data
        self.process_dates()  # Convert and validate the date format
        self.sort_data()  # Sort the data by date and category
        self.display_data()  # Display the cleaned and categorized data
        self.display_monthly_category_totals()  # Display monthly category totals


saving_csv_file_path = "/Users/drewdrummond/Documents/coding projects/Python_expense_tracker/CSV's/saving.csv"
tracker = SavingsTracker(saving_csv_file_path)
tracker.run()