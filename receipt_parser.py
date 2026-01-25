import re
import pandas as pd
from googletrans import Translator
import unicodedata

# ----------------------------
# Helper functions
# ----------------------------
def simplify_name(name):
    """Lowercase, remove accents, punctuation, and stopwords"""
    name = name.lower()
    name = ''.join(c for c in unicodedata.normalize('NFD', name)
                   if unicodedata.category(c) != 'Mn')
    stopwords = ['tray', 'eco', "safata", "pantry"]
    pattern = r'\b(' + '|'.join(stopwords) + r')\b'
    name = re.sub(pattern, '', name)
    name = re.sub(r'[^a-z0-9\s]', '', name)
    return ' '.join(name.split())

def cleanup_text(text):
    """Cleans up raw receipt text into a list of lines"""
    lines = text.split('\n')
    cleaned_lines = []
    curr_line = ''

    for line in lines:
        line = line.strip()
        if line:
            if line[0].isalpha():
                if curr_line:
                    cleaned_lines.append(curr_line)
                cleaned_lines.append(line)
                curr_line = ""

            else:
                 curr_line += line

    if curr_line:
        cleaned_lines.append(curr_line)

    return cleaned_lines


def extract_items(lines):
    """Extract item names, prices, from messy receipt text"""
    items = []
    i = 0
    while i < len(lines)-1:
        name = lines[i]
        price = None
        #price is on next line
        price_line = lines[i+1]
        price_match = re.search(r'(\d+[.,]?\d{0,2})', price_line)
        if price_match:
            price_str = price_match.group(1).replace(',', '.')
            try:
                price = float(price_str)
            except ValueError:
                price = None

            i += 2  # move to next item

        if price is not None:
            items.append({
                'original_name': name,
                'price': price
            })
        else:
            print(f"Could not find price for item: {name}")

       
    return items

def translate_items(items, src='ca', dest='en'):
    translator = Translator()
    for item in items:
        try:
            translated = translator.translate(item['original_name'], src=src, dest=dest)
            item['translated_name'] = translated.text
        except Exception:
            item['translated_name'] = item['original_name']  # fallback
        item['simple_name'] = simplify_name(item['translated_name'])
    return items

def get_items_from_receipt_text(text):
    lines = cleanup_text(text)
    print("Cleaned lines:", lines)
    # Extract + translate + simplify
    items = extract_items(lines)
    items = translate_items(items)
    df = pd.DataFrame(items)[['simple_name','price','original_name']]
    df.to_csv('receipts/parsed_receipt.csv', index=False)
    return df


if __name__ == '__main__':
    # ----------------------------
    # Example usage
    # ----------------------------
    raw_text = """P. HIGIENIC COMPACTE

    2,25 € 4
    LLIMA SAFATA

    0,99 
    € 2
    CORIANDRE FRESC ECO
    1,19
    €
    3
    XOCOLATA NEGRE REBOSTE
    2,29
    € 
    3"""

    lines = cleanup_text(raw_text)
    print("Cleaned lines:", lines)
    # Extract + translate + simplify
    items = extract_items(lines)
    items = translate_items(items)

    # Convert to DataFrame for easy import into Google Sheets
    df = pd.DataFrame(items)[['simple_name','price','translated_name','original_name']]
    print(df.to_string(index=False))
