from flask import Flask, request, jsonify, render_template
from PIL import Image
from pyzbar.pyzbar import decode, ZBarSymbol
import os
from online_barcode_search import lookup_product_openfoodfacts
from receipt_parser import get_items_from_receipt_text
import pandas as pd
from match_prices import fuzzy_match_prices
from save_to_sheets import save_to_google_sheets
import time


app = Flask(__name__)

# Delet decoded_barcodes.csv on startup
def delete_decoded_barcodes():
    file_path = 'receipts/decoded_barcodes.csv'
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Deleted existing file: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parse_receipt', methods=['POST'])
def parse_receipt():
    """Handles receipt text uploads from users."""
    if not request.is_json:
        return jsonify({'error': 'Invalid input, JSON expected'}), 400

    data = request.get_json()
    receipt_text = data.get('text', '')

    if not receipt_text:
        return jsonify({'error': 'No receipt text provided'}), 400

    df = get_items_from_receipt_text(receipt_text)

    # Convert DataFrame to list of dicts for JSON response
    items = df.to_dict(orient='records')

    return jsonify({'items': items}), 200

@app.route("/save_to_sheets", methods=["POST"])
def save_to_sheets():
    
    try:
        result_df = fuzzy_match_prices(threshold=60)
        save_to_google_sheets(result_df)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

    return jsonify({'status': 'success', 'message': 'Data saved to Google Sheets (stub)'}), 200


@app.route("/upload", methods=["POST"])
def upload_file():
    """Handles image uploads from users."""
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400
    
    file_path = os.path.join("img", file.filename)
    file.save(file_path)

    print(f"File saved: {file_path}")


    # Decode image bytes into OpenCV image
    #file is now at img/file.filename
    img = Image.open('img/image.jpg')

    if img is None:
        return jsonify({'error': 'could not decode image'}), 400

    decoded_list = decode(img)

    # For each detected barcode, attempt a product lookup (best-effort)
    products_df = pd.DataFrame(columns=['barcode', "product_name", "size", "calories", "fat", "protein", "carbohydrates", "fiber", "sugars"])
    for bcode in decoded_list:
        product = []
        product_code = bcode.data.decode("utf-8")
        print(product_code)
        product.append(product_code)
        # simple numeric barcodes are the typical UPC/EAN formats
        #product_info = lookup_product_openfoodfacts(code)
        #b['product'] = product_info

        product_dict = lookup_product_openfoodfacts(product_code)
        if not product_dict:
            continue

        product.append(product_dict["product_name"])
        num_servings = product_dict.get('quantity')  # Default to 1 if quantity is missing or zero
        if not num_servings:
            num_servings = 1
        product.append(num_servings)

        macro_values = product_dict.get('macros_per100', {})
        product.append(macro_values.get('calories'))
        product.append(macro_values.get('fat'))
        product.append(macro_values.get('protein'))
        product.append(macro_values.get('carbohydrates'))
        product.append(macro_values.get('fiber'))
        product.append(macro_values.get('sugars'))
        products_df = pd.concat([products_df, pd.DataFrame([product], columns=products_df.columns)], ignore_index=True)

    if products_df.empty:
        return jsonify({'error': 'no barcodes found'}), 400
    
    # Save to CSV with append mode
    file_exists = os.path.exists('receipts/decoded_barcodes.csv')
    products_df.to_csv('receipts/decoded_barcodes.csv', mode='a', header=not file_exists, index=False)
    
    return jsonify(products_df.to_dict(orient='records')), 200

if __name__ == '__main__':
    delete_decoded_barcodes()
    app.run(host='0.0.0.0', port=5000)
