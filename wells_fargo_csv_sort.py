# Importing necessary libraries
import pandas as pd
import re

class ExpenseTracker:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.categories = {
            'food': [
                r'MCDONALD\S*', r'TACO BELL', r'CHICK-FIL-A', r'OLIVE GARDEN', 
                r'7-ELEVEN', r'CHIPOTLE', r'CULVERS', r'CHINA TASTE', r'SARASOTA BOBA TEA',
                r'DAIRY QUEEN', r'TST\* THE MELTING POT', r'FIRST WATCH', r'TARGET\.COM',
                r'DING TEA', r'SQ \*SIESTA KEY FUDGE FAC', r'WAWA', r'3 NATIVES', r'PY \*PDQ', 
                r'DUNKIN', r'DETWILER\'S FARM MARKET', r'PEI WEI', r'NORI JAPANESE AND THAI R', 
                r'TST\* South Philly Cheeses', r'DD/BR #350919 Q35', r'POPEYES', r'MICHELANGELO', 
                r'JA RAMEN', r'SUPER BUFFET', r'TST\* South Philly CheesesBradenton FL', 
                r'PETCO 2710 SARASOTA FL', r'TARGET 00020347 SARASOTA FL', r'PUBLIX', r'TEA', r'CRUMBL', r'SMOOTHIE'  # Food and grocery stores
            ],
            'material': [
                r'CHEGG ORDER', r'IBI\*FABLETICS.COM', r'KOHL\'S', r'DICK\'S Sporting Goods', 
                r'EDGEFIELD GIFT SHOP', r'TACOS GONE MOBILE LLC', r'CARIBOU # EINSTEIN #3649',
                r'BIG DANS CAR WASH BRADENBRADENTON FL', r'PETCO 2710 SARASOTA FL', r'BJJ'  # Clothes, personal items, and car wash
            ],
            'gas': [
                r'EXXON', r'SHELL OIL', r'76 - SEI 35335', r'WAWA'  # Gas stations
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
                r'K1 SPEED - TAMPA, FL TAMPA FL', r'AMF'  # Entertainment and recreational activities
            ],
            'reoccuring': [
                r'ONLINE PAYMENT THANK YOU', r'GITHUB', r'AMZN Mktp US', 
                r'PHOTOENFORCEMENT PROGRAM', r'PYTHONANYWHERE', r'THANK YOU'  # Subscription and regular services
            ]}
   

    def load_csv(self):
        try:
            self.df = pd.read_csv(self.file_path, header=None, names=['Date y/m/d', 'Amount', 'Symbol', 'Symbol2', 'Description'])
            print("CSV file loaded successfully.")
        except Exception as e:
            print(f"Error loading CSV file: {e}")

    def clean_data(self):
        # Keep only relevant columns
        self.df = self.df[['Date y/m/d', 'Amount', 'Description']]

        # Clean the Amount column
        self.df['Amount'] = self.df['Amount'].replace('[^\d.-]', '', regex=True)
        self.df['Amount'] = self.df['Amount'].replace('', pd.NA)
        self.df['Amount'] = pd.to_numeric(self.df['Amount'], errors='coerce')
    

    def categorize_transaction(self, description):
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if re.search(keyword, description, re.IGNORECASE):  # Case-insensitive search
                    return category
        return 'other'  # Default category if no match is found

    def apply_categorization(self):
        self.df['Category'] = self.df['Description'].apply(lambda x: self.categorize_transaction(x))

    def process_dates(self):
        self.df['Date y/m/d'] = pd.to_datetime(self.df['Date y/m/d'], errors='coerce', infer_datetime_format=True)
        self.df = self.df.dropna(subset=['Date y/m/d'])
        self.df['Date y/m/d'] = self.df['Date y/m/d'].dt.date

    def sort_data(self):
        self.df = self.df.sort_values(by=['Date y/m/d', 'Category'])

    def display_data(self):
        pd.set_option('display.max_rows', None)  # Show all rows
        pd.set_option('display.max_columns', None)  # Show all columns
        pd.set_option('display.width', None)  # Adjust the width to avoid line breaks
        pd.set_option('display.max_colwidth', None)  # Show full column content
        print("\nCredit Card Transactions Sorted by Date and Category:\n")
        print(self.df)

    def run(self):
        self.load_csv()
        self.clean_data()
        self.apply_categorization()
        self.process_dates()
        self.sort_data()
        self.display_data()

# Instantiate and run the ExpenseTracker
credit_csv_file_path = "/Users/drewdrummond/Documents/coding projects/Python_expense_tracker/CSV's/new_credit.csv"
tracker = ExpenseTracker(credit_csv_file_path)
tracker.run()

