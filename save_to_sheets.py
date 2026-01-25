import gspread
from oauth2client.service_account import ServiceAccountCredentials

def save_to_google_sheets(df, workbook_name="Food Tracking", sheet_name="Receipts"):
    # Authenticate
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)

    # Open your sheet
    sheet = client.open(workbook_name).worksheet(sheet_name)

    # Push the data (overwrite range)
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("Data saved to Google Sheets successfully.")
    return

if __name__ == '__main__':
    import pandas as pd

    # Example DataFrame
    df = pd.read_csv('receipts/matched_products.csv')

    # Save to Google Sheets
    save_to_google_sheets(df)