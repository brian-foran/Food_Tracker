from flask import Flask, request, jsonify, send_from_directory
import cv2
import numpy as np
from pyzbar import pyzbar
import requests

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    """Serve the mobile-friendly upload UI (static/index.html)."""
    return send_from_directory('static', 'index.html')


def decode_barcodes(image):
    """Decode barcodes/QR codes from an OpenCV image using pyzbar.

    Returns a list of dicts with keys: data, type, rect, polygon
    """
    barcodes = pyzbar.decode(image)
    results = []
    for b in barcodes:
        try:
            data = b.data.decode('utf-8')
        except Exception:
            data = b.data

        rect = {
            'left': int(b.rect.left),
            'top': int(b.rect.top),
            'width': int(b.rect.width),
            'height': int(b.rect.height)
        }

        polygon = []
        if hasattr(b, 'polygon') and b.polygon:
            for p in b.polygon:
                polygon.append({'x': int(p.x), 'y': int(p.y)})

        results.append({
            'data': data,
            'type': b.type,
            'rect': rect,
            'polygon': polygon
        })

    return results




@app.route('/upload', methods=['POST'])
def upload():
    # Expecting a multipart/form-data POST with an "image" file field
    if 'image' not in request.files:
        return jsonify({'error': 'no image file in request'}), 400

    file = request.files['image']
    data = file.read()
    if not data:
        return jsonify({'error': 'empty file'}), 400

    # Decode image bytes into OpenCV image
    nparr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return jsonify({'error': 'could not decode image'}), 400

    height, width = img.shape[:2]

    barcodes = decode_barcodes(img)

    # For each detected barcode, attempt a product lookup (best-effort)
    for b in barcodes:
        code = b['data']
        # simple numeric barcodes are the typical UPC/EAN formats
        #product_info = lookup_product_openfoodfacts(code)
        #b['product'] = product_info

    return jsonify({'width': width, 'height': height, 'barcodes': barcodes})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
