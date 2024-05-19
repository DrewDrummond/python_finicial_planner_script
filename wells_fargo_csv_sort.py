import pandas as pd  # Pandas is a powerful data manipulation library
import re  # The re module provides support for regular expressions

class ExpenseTracker:
    def __init__(self, file_path):
        self.file_path = file_path  # Path to the CSV file containing the transaction data
        self.df = None  # DataFrame to store the transaction data
        # Dictionary to categorize transactions based on keywords in the description
        self.categories = {
            'food': [
                r'MCDONALD\S*', r'TACO BELL', r'CHICK-FIL-A', r'OLIVE GARDEN', 
                r'7-ELEVEN', r'CHIPOTLE', r'CULVERS', r'CHINA TASTE', r'SARASOTA BOBA TEA',
                r'DAIRY QUEEN', r'TST\* THE MELTING POT', r'FIRST WATCH', r'TARGET\.COM',
                r'DING TEA', r'SQ \*SIESTA KEY FUDGE FAC', r'WAWA', r'3 NATIVES', r'PY \*PDQ', 
                r'DUNKIN', r'DETWILER\'S FARM MARKET', r'PEI WEI', r'NORI JAPANESE AND THAI R', 
                r'TST\* South Philly Cheeses', r'DD/BR #350919 Q35', r'POPEYES', r'MICHELANGELO', 
                r'JA RAMEN', r'SUPER BUFFET', r'TST\* South Philly CheesesBradenton FL', 
                r'PETCO 2710 SARASOTA FL', r'TARGET 00020347 SARASOTA FL', r'PUBLIX', r'TEA', r'CRUMBL', r'SMOOTHIE'  # Keywords for food category
            ],
            'material': [
                r'CHEGG ORDER', r'IBI\*FABLETICS.COM', r'KOHL\'S', r'DICK\'S Sporting Goods', 
                r'EDGEFIELD GIFT SHOP', r'TACOS GONE MOBILE LLC', r'CARIBOU # EINSTEIN #3649',
                r'BIG DANS CAR WASH BRADENBRADENTON FL', r'PETCO 2710 SARASOTA FL', r'BJJ'  # Keywords for material category
            ],
            'gas': [
                r'EXXON', r'SHELL OIL', r'76 - SEI 35335', r'WAWA'  # Keywords for gas category
            ],
            'entertainment': [
                r'HI TEC PAINTBALL PARK', r'K1 SPEED TAMPA', r'THE MELTING POT', 
                r'PAR\'SMOOTHIE KING', r'RACETRAC', r'K1 SPEED',
                r'DAIQUIRI DECK INC', r'REG HOLLYWOOD', r'SUNCOAST GOLF CENTER',
                r'SQ \*CHAMPAGNE POETRY PATI', r'MULTNOMAH FALLS BRIDAL VEIL',
                r'MSP AIRP LEEANN CHIN', r'SQ \*ROCKY MOUNTAIN CHOCOL', r'ROASTED NUTS LLC',
                r'WDW POPCORN CARTS LAKE BUENA VIFL', r'DISNEY MK PARKING LAKE BUENA VIFL',
                r"WDW PRINCE ERIC'S LAKE BUENA VIFL", r'WDW POPCORN CARTS LAKE BUENA VIFL',
                r'WDW ICE CREAM CARTS LAKE BUENA VIFL', r'WDW WESTWARD HO LAKE BUENA VIFL',
                r'WDW SLEEPY HOLLOW 407-828-5630 FL', r'WDW CHESHIRE CAFE LAKE BUENA VIFL',
                r'WDW THE FRIARS NOOK LAKE BUENA VIFL', r'DISNEY ST PARKING LAKE BUENA VIFL',
                r'WDW MILK STAND LAKE BUENA VIFL', r"WDW ROSIE'S 407-828-5630 FL",
                r'WDW RONTO ROASTERS 407-828-5630 FL', r"WDW KATSAKA'SKETTLE LAKE BUENA VIFL",
                r'WDW CHURRO CART LAKE BUENA VIFL', r"WDW OGA'S CANTINA LAKE BUENA VIFL",
                r'RACETRAC100 00001008 BRADENTON FL', r'DAIQUIRI DECK INC SARASOTA FL',
                r'K1 SPEED - TAMPA, FL TAMPA FL', r'AMF'  # Keywords for entertainment category
            ],
            'reoccuring': [
                r'GITHUB', r'AMZN Mktp US', 
                r'PHOTOENFORCEMENT PROGRAM', r'PYTHONANYWHERE',  # Keywords for reoccurring category
            ],
            'credit card payment': [r'ONLINE PAYMENT THANK YOU', r'AUTOMATIC PAYMENT']  # Keywords for credit card payment category
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
        # Check each description against the keywords in each category
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if re.search(keyword, description, re.IGNORECASE):  # Case-insensitive search using regex
                    return category
        return 'other'  # Default category if no match is found

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
            
            # Print monthly totals at the end
            monthly_totals = self.display_monthly_totals(grouped)
            print("\nMonthly totals:\n")
            for total in monthly_totals:
                print(total)
        else:
            print("Date conversion failed; check data format.")

    # Add this method to calculate and display the amount and percentage spent on each category for each month
    def display_monthly_category_totals(self, grouped):
        for name, group in grouped:
            print(f"\nCategory Totals and Percentages for {name}:\n")
            
            total_spent = group['Amount'][group['Amount'] < 0].sum()  # Calculate total spent for the month
            category_totals = group[group['Amount'] < 0].groupby('Category')['Amount'].sum()  # Calculate total spent per category for the month
            
            # Calculate percentage spent per category for the month
            category_percentages = (category_totals / total_spent) * 100
            
            # Print the totals and percentages for each category for the month
            for category, total in category_totals.items():
                percentage = category_percentages[category]
                print(f"Category: {category}, Total Spent: ${total:.2f}, Percentage: {percentage:.2f}%")

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
