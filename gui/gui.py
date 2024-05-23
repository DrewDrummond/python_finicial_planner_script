import tkinter as tk
from tkinter import scrolledtext, filedialog
import sys
from pathlib import Path
from trackers.Checking_tracker import CheckingTracker
from trackers.Credit_tracker import CreditTracker
from trackers.Savings_tracker import SavingsTracker


class TrackerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Account Tracker")

        # Configure the grid
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=0)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=1)
        
        # Text box for output
        self.output_txt = scrolledtext.ScrolledText(master, width=70, height=20)
        self.output_txt.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="nsew")

        # Button to choose a file
        self.choose_file_btn = tk.Button(master, text="Choose File", command=self.choose_file)
        self.choose_file_btn.grid(row=1, column=0, pady=10, padx=10, sticky="ew")

        # Button to run the tracker
        self.run_btn = tk.Button(master, text="Run Tracker", command=self.run_tracker)
        self.run_btn.grid(row=1, column=1, pady=10, padx=10, sticky="ew")

        # Button to clear the output
        self.clear_btn = tk.Button(master, text="Clear Output", command=self.clear_output)
        self.clear_btn.grid(row=1, column=2, pady=10, padx=10, sticky="ew")

        # Variable to store the chosen file path
        self.file_path = None

    def choose_file(self):
        # Open a file dialog to choose the CSV file
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.file_path = file_path
            file_name = Path(file_path).name  # Extracts only the file name from the path
            self.output_txt.insert(tk.END, f"Selected file: {file_name}\n")  # Display only the file name

    def run_tracker(self):
        if self.file_path and Path(self.file_path).exists():
            file_name = Path(self.file_path).stem
            tracker_class = self.get_tracker_class(file_name)
            if tracker_class:
                tracker = tracker_class(self.file_path)
                tracker.run()
                # Redirect the print statements from your tracker to the text widget
                original_stdout = sys.stdout  # Save a reference to the original standard output
                sys.stdout = self.TextRedirector(self.output_txt)
                tracker.display_data()
                sys.stdout = original_stdout  # Reset the standard output to its original value
            else:
                self.output_txt.insert(tk.END, f"No tracker class found for file: {file_name}\n")
        else:
            self.output_txt.insert(tk.END, "Please select a valid CSV file or check the file path.\n")

    def get_tracker_class(self, file_name):
        # Determine the appropriate tracker class based on the file name
        if 'checking' in file_name.lower():
            return CheckingTracker
        elif 'credit' in file_name.lower():
            return CreditTracker
        elif 'savings' in file_name.lower():
            return SavingsTracker
        return None

    def clear_output(self):
        self.output_txt.delete(1.0, tk.END)

    class TextRedirector:
        def __init__(self, text_widget):
            self.text_widget = text_widget

        def write(self, str):
            self.text_widget.insert(tk.END, str)

        def flush(self):
            pass

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")  # Default size of the window
    app = TrackerGUI(root)
    root.mainloop()