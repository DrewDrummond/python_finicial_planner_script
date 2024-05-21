import pandas as pd
import re

class ExpenseTracker:
    def __init__(self, file_path):
        self.file_path = file_path  # Path to the CSV file containing the transaction data
        self.df = None  # DataFrame to store the transaction data
        # Dictionary to categorize transactions based on keywords in the description
        self.categories = {
            'food': [
                r'mcdonald\'s', r'taco bell', r'chick-fil-a', r'olive garden', 
                r'7-eleven', r'chipotle', r'culvers', r'china taste', r'sarasota boba tea',
                r'dairy queen', r'tst\* the melting pot', r'first watch', r'target\.com',
                r'ding tea', r'sq \*siesta key fudge fac', r'wawa', r'3 natives', r'py \*pdq', 
                r'dunkin', r'detwiler\'s farm market', r'pei wei', r'nori japanese and thai r', 
                r'tst\* south philly cheeses', r'dd/br #350919 q35', r'popeyes', r'michelangelo', 
                r'ja ramen', r'super buffet', r'tst\* south philly cheesesbradenton fl', 
                r'petco 2710 sarasota fl', r'target 00020347 sarasota fl', r'publix', r'tea', r'crumbl', r'smoothie'
            ],
            'material': [
                r'chegg order', r'ibi\*fabletics.com', r'kohl\'s', r'dick\'s sporting goods', 
                r'edgefield gift shop', r'tacos gone mobile llc', r'caribou # einstein #3649',
                r'big dans car wash bradenbradenton fl', r'petco 2710 sarasota fl', r'bjj'
            ],
            'gas': [
                r'exxon', r'shell oil', r'76 - sei 35335', r'wawa'
            ],
            'entertainment': [
                r'hi tec paintball park', r'k1 speed tampa', r'the melting pot', 
                r'par\'smoothie king', r'racetrac', r'k1 speed', r'daiquiri deck inc', 
                r'reg hollywood', r'suncoast golf center', r'sq \*champagne poetry pati', 
                r'multnomah falls bridal veil', r'msp airp leeann chin', r'sq \*rocky mountain chocol', 
                r'roasted nuts llc', r'wdw popcorn carts lake buena vifl', r'disney mk parking lake buena vifl', 
                r"wdw prince eric's lake buena vifl", r'wdw popcorn carts lake buena vifl', r'wdw ice cream carts lake buena vifl', 
                r'wdw westward ho lake buena vifl', r'wdw sleepy hollow 407-828-5630 fl', r'wdw cheshire cafe lake buena vifl', 
                r'wdw the friars nook lake buena vifl', r'disney st parking lake buena vifl', r'wdw milk stand lake buena vifl', 
                r"wdw rosie's 407-828-5630 fl", r'wdw ronto roasters 407-828-5630 fl', r"wdw katsaka'skettle lake buena vifl", 
                r'wdw churro cart lake buena vifl', r"wdw oga's cantina lake buena vifl", r'racetrac100 00001008 bradenton fl', 
                r'daiquiri deck inc sarasota fl', r'k1 speed - tampa, fl tampa fl', r'amf'
            ],
            'reoccuring': [
                r'github', r'amzn mktp us', 
                r'photoenforcement program', r'pythonanywhere'
            ],
            'credit card payment': [r'online payment thank you', r'automatic payment']
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

    def sort_data(self):
        # Sort the DataFrame by date and category
        self.df = self.df.sort_values(by=['Date y/m/d', 'Category'])  # Sort by date and then by category

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
        if self.df['Date y/m/d'].dtype == '<M8[ns]':  # '<M8[ns]' indicates datetime64[ns] dtype
            self.df['YearMonth'] = self.df['Date y/m/d'].dt.to_period('M')  # Extract YearMonth period from date
            grouped = self.df.groupby('YearMonth')  # Group the DataFrame by YearMonth
            
            # Print transactions for each month
            for name, group in grouped:
                print(f"\nTransactions for {name}:\n")
                print(group[['Date y/m/d', 'Amount', 'Description', 'Category']])
            
            # Print monthly category totals and percentages
            self.display_monthly_category_totals(grouped)
            
        else:
            print("Date conversion failed; check data format.")

    def display_monthly_category_totals(self, grouped):
        """
        Calculate and display the amount and percentage spent on each category for each month.
        """
        for name, group in grouped:
            print(f"\nTotal spent in {name}: ${group['Amount'][group['Amount'] < 0].sum():.2f}")
            total_spent = group['Amount'][group['Amount'] < 0].sum()  # Calculate total spent for the month
            category_totals = group[group['Amount'] < 0].groupby('Category')['Amount'].sum()  # Calculate total spent per category for the month
            
            # Calculate percentage spent per category for the month
            category_percentages = (category_totals / total_spent) * 100
            
            # Print the totals and percentages for each category for the month
            for category, total in category_totals.items():
                percentage = category_percentages[category]
                print(f"    - {category}: ${abs(total):.2f}, = {percentage:.2f}%")  # Indent for better readability

    def run(self):
        # Run all the methods in sequence to process and display the data
        self.load_csv()  # Load the data from the CSV file
        self.clean_data()  # Clean the data to ensure it's in the right format
        self.apply_categorization()  # Categorize each transaction
        self.process_dates()  # Convert and validate the date format
        self.sort_data()  # Sort the data by date and category
        self.display_data()  # Display the processed data and monthly totals

# Instantiate and run the ExpenseTracker
credit_csv_file_path = "/Users/drewdrummond/Documents/coding projects/Python_expense_tracker/CSV's/new_credit.csv"
tracker = ExpenseTracker(credit_csv_file_path)
tracker.run()
