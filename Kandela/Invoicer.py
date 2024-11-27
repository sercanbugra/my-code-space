import pandas as pd
from openpyxl import load_workbook
import win32com.client as win32
import os
from tqdm import tqdm
import sys  # Import the sys module

# Paths to files
kandela_path = 'Kandela_2024.xlsx'
output_folder = 'output'
os.makedirs(output_folder, exist_ok=True)

# Load the data from Kandela.xlsx
data = pd.read_excel(kandela_path)

# Loop through each row in the Kandela file with a progress bar
for index, row in tqdm(data.iterrows(), total=len(data), desc="Generating PDF Invoices", file=sys.stdout):
    # Determine the correct template based on currency columns
    if pd.notna(row['TRY']):
        invoice_template_path = 'invoice.xlsx'
    elif pd.notna(row['Pound']):
        invoice_template_path = 'Invoice_Pound.xlsx'
    elif pd.notna(row['Euro']):
        invoice_template_path = 'Invoice_Euro.xlsx'
    else:
        print(f"Skipping row {index + 1} due to missing currency values.")
        continue  # Skip rows without any currency value

    # Open the correct invoice template
    workbook = load_workbook(invoice_template_path)
    sheet = workbook.active
    
    # Map Kandela columns to invoice cells
    sheet['D4'].value = row['DATE']
    sheet['D7'].value = row['Inv No']
    sheet['A9'].value = row['Name']
    
    # Set the currency value in the template based on the detected currency column
    if pd.notna(row['TRY']):
        sheet['D15'].value = row['TRY']
    elif pd.notna(row['Pound']):
        sheet['D15'].value = row['Pound']
    elif pd.notna(row['Euro']):
        sheet['D15'].value = row['Euro']
        
    sheet['C15'].value = row['Hours']
    
    # Format the date and determine the folder based on the month
    date_str = pd.to_datetime(row['DATE']).strftime('%d.%m')
    month_folder = pd.to_datetime(row['DATE']).strftime('%m')  # Month as folder name

    # Create a subfolder based on the month
    subfolder_path = os.path.join(output_folder, month_folder)
    os.makedirs(subfolder_path, exist_ok=True)

    # Generate filename and output path
    filename = f"{row['Name']} - {date_str}.pdf"
    output_path = os.path.join(subfolder_path, filename)
    
    # Save the modified invoice file as a temporary Excel file
    temp_invoice_path = 'temporary_invoice2.xlsx'
    workbook.save(temp_invoice_path)
    workbook.close()
    
    # Convert the Excel to PDF using win32com
    excel = win32.Dispatch("Excel.Application")
    excel.Visible = False
    wb = excel.Workbooks.Open(os.path.abspath(temp_invoice_path))
    wb.ExportAsFixedFormat(0, os.path.abspath(output_path))  # 0 is for PDF format
    wb.Close(False)
    excel.Quit()
    
    # Remove the temporary Excel file
    os.remove(temp_invoice_path)

# Completion message
print("PDF generation complete. Files are saved in classified folders under 'output'.")
