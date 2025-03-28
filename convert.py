import pandas as pd

# Load the Excel file
xlsx_file = "static/csv/data.xlsx"  # Change this to your file
csv_file = "static/csv/output.csv"  # Output file

# Read the Excel file
df = pd.read_excel(xlsx_file, engine='openpyxl')

# Save as CSV
df.to_csv(csv_file, index=False)

print(f"Converted {xlsx_file} to {csv_file}")
