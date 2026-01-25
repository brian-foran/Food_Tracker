import requests

def lookup_product_openfoodfacts(barcode):
    """Lookup a barcode at OpenFoodFacts. Returns product info dict or None.

    Uses the public OpenFoodFacts API which works well for food items (EAN/UPC).
    If the product isn't found, returns None. On network errors returns a dict
    with an "error" key.
    """
    url = f'https://world.openfoodfacts.org/api/v0/product/{barcode}.json'
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return None

        data = resp.json()
        # OpenFoodFacts returns status=1 when product found
        if data.get('status') == 1:          
            p = data.get('product')
            if not p:
                raise ValueError("No product field in response")
            

            nutriments = {k: v for k, v in p.get('nutriments', {}).items() if k.endswith('_100g')}
            quantity = "".join(i for i in p.get('quantity', []) if i.isdigit() or i == '.')
            return {
                'product_name': p.get('product_name'),
                #'brands': p.get('brands'),
                #'categories': p.get('categories'),
                #'image_url': p.get('image_url'),
                'quantity': 0 if not quantity else float(quantity),
                'nutriments': nutriments,
                'macros_per100': {
                    'calories': nutriments.get('energy-kcal_100g'),
                    'protein': nutriments.get('proteins_100g'),
                    'fat': nutriments.get('fat_100g'),
                    'carbohydrates': nutriments.get('carbohydrates_100g'),
                    'fiber': nutriments.get('fiber_100g'),
                    'sugars': nutriments.get('sugars_100g'),
                    }
            }
        raise ValueError("Product not found")
    except Exception as e:
        return {'error': str(e)}
    
if __name__ == '__main__': 
    # Example usage
    barcode = '2350385002419'  # Example barcode for a food product
    product_info = lookup_product_openfoodfacts(barcode)
    if product_info:
        print("Product found: ", product_info.get('product_name'))
        print(product_info)
        print(product_info.get('product_name', 'Name Field Missing'))
        macros_per100 = product_info.get('macros_per100', 'nutrients missing')
        print(macros_per100)
        quantity = product_info.get('quantity')
        print(quantity)
        #format nutriments nicely
        if quantity:
            total_macros = {k: v * (float(quantity) / 100) for k, v in macros_per100.items()}
            print(total_macros)

    else:
        print("Product not found.")