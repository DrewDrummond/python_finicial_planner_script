# importing my librairies   
import pandas as pd
import re


file_path = "/Users/drewdrummond/Documents/coding projects/Python_expense_tracker/CSV's/new_credit.csv" # path to the csv file saved as a variable
df = pd.read_csv(file_path, header=None, names=['Date', 'Amount', 'Symbol', 'Description']) # reading the csv file and assigning the columns names


# creating a function to sort the data
categories = {

}

