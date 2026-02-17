# Food App - Barcode lookup over HTTP

This simple Flask app accepts an image upload (multipart/form-data, field name `image`) at `/upload`, decodes barcodes/QR codes using `pyzbar` + OpenCV, and performs a best-effort lookup using the OpenFoodFacts API.

## To Do
1. Add food nutrition lookup inside sheets
2. Save all uploaded receipts for backup price checking
3. Upload all data from receipt, not just matches

Quick start (Windows PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python server.py
```

Example request (using curl):

```powershell
curl -X POST -F "image=@C:\path\to\photo.jpg" http://localhost:5000/upload
```

The response JSON contains image width/height and a `barcodes` array with decoded data and optional `product` info.


## Receipt Parser Info
* Use Iphone to scan text from receipt, then paste into website, creates a csv of items and cost

## Next steps
1. Use pip install gspread oauth2client to push the created csv into my FOOD Tracking Google Doc
2. Update online_barcode search to create a csv that matches my food tracking format and also use gspread to push newly scanned foods to the FOODS sheet of the document
3. Make a comparison function that correctly matches the nutrition facts from the barcode with the price from the receipt so that it can be uploaded to the sheet as a single Post.
