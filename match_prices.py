import pandas as pd
from thefuzz import fuzz
from thefuzz import process
from googletrans import Translator
import re
import unicodedata


def preprocess_name(name):
    """Normalize and clean product names for better matching"""
    name = str(name).lower()
    
    # Remove accents/diacritics
    name = ''.join(c for c in unicodedata.normalize('NFD', name)
                   if unicodedata.category(c) != 'Mn')
    
    # Remove measurements and quantities (1kg, 500g, 2l, etc.)
    name = re.sub(r'\d+\s*(kg|g|l|ml|cl|oz|lb|pack|u)', '', name, flags=re.IGNORECASE)
    
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    return name.strip()


def fuzzy_match_prices(decoded_csv='receipts/decoded_barcodes.csv', 
                       parsed_csv='receipts/parsed_receipt.csv',
                       output_csv='receipts/matched_products.csv',
                       threshold=50):
    """
    Fuzzy matches products from decoded barcodes with parsed receipt items
    and adds prices to the barcode data.
    
    Args:
        decoded_csv: Path to decoded barcodes CSV
        parsed_csv: Path to parsed receipt CSV
        output_csv: Path to save matched results
        threshold: Minimum fuzzy matching score (0-100)
    """
    
    # Read both CSV files
    try:
        barcodes_df = pd.read_csv(decoded_csv)
        receipt_df = pd.read_csv(parsed_csv)
    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}")
        return None
    
    print(f"Loaded {len(barcodes_df)} barcode products")
    print(f"Loaded {len(receipt_df)} receipt items")
    
    # Add price column to barcodes dataframe
    barcodes_df['matched_price'] = None
    barcodes_df['match_score'] = None
    barcodes_df['matched_receipt_name'] = None
    barcodes_df['english_name'] = None
    barcodes_df['portion_size'] = None
    
    # Create a list of receipt items to match against
    # Try multiple name columns that might exist in parsed_receipt
    if 'original_name' in receipt_df.columns:
        receipt_names = receipt_df['original_name'].tolist()
        name_col = 'original_name'
    # elif 'translated_name' in receipt_df.columns:
    #     receipt_names = receipt_df['translated_name'].tolist()
    #     name_col = 'translated_name'
    else:
        receipt_names = receipt_df.iloc[:, 0].tolist()  # Use first column as fallback
        name_col = receipt_df.columns[0]
    
    print("List of receipt names:", receipt_names)

    # Preprocess receipt names for better matching
    preprocessed_receipt_names = [preprocess_name(name) for name in receipt_names]

    # For each barcode product, find best match in receipt
    for idx, row in barcodes_df.iterrows():
        product_name = str(row['product_name']).lower()
        product_name_ca = translate_name(product_name, src='es', dest='ca').lower()

        print(f"\nMatching for product: '{product_name}' (Catalan: '{product_name_ca}')")
        
        # Preprocess the product name
        processed_product = preprocess_name(product_name_ca)
        print(f"Preprocessed: '{processed_product}'")
        
        # Try multiple scoring methods and pick the best
        matches = []
        
        # Method 1: Token sort ratio on preprocessed names
        for i, receipt_name in enumerate(preprocessed_receipt_names):
            score1 = fuzz.token_sort_ratio(processed_product, receipt_name)
            matches.append((receipt_name, score1, i, 'token_sort'))
            
            score2 = fuzz.partial_ratio(processed_product, receipt_name)
            matches.append((receipt_name, score2, i, 'partial'))
            
            score3 = fuzz.token_set_ratio(processed_product, receipt_name)
            matches.append((receipt_name, score3, i, 'token_set'))
        
        # Pick the best match across all methods
        if matches:
            best_match = max(matches, key=lambda x: x[1])
            matched_name_processed, score, matched_idx, method = best_match
            
            print(f"Best match using {method}: '{preprocessed_receipt_names[matched_idx]}' (score: {score})")
        
        if matches and best_match[1] >= threshold:
            matched_idx = best_match[2]
            score = best_match[1]
            
            # Get the original receipt name (not preprocessed)
            original_matched_name = receipt_names[matched_idx]
            
            # Get the price from the matched receipt item
            matched_price = receipt_df.iloc[matched_idx]['price']
            
            # Update the dataframe
            barcodes_df.at[idx, 'matched_price'] = matched_price
            barcodes_df.at[idx, 'match_score'] = score
            barcodes_df.at[idx, 'matched_receipt_name'] = original_matched_name
            product_name_en = translate_name(product_name, src='es', dest='en').lower()
            barcodes_df.at[idx, 'english_name'] = product_name_en

            
            print(f"✓ Matched '{product_name_ca}' with '{original_matched_name}' (score: {score}) - Price: €{matched_price}")
        else:
            print(f"✗ No match found for '{product_name_ca}'")
            #still update the dataframe, just with None values
            barcodes_df.at[idx, 'matched_price'] = None
            barcodes_df.at[idx, 'match_score'] = None
            barcodes_df.at[idx, 'matched_receipt_name'] = None
            product_name_en = translate_name(product_name, src='es', dest='en').lower()
            barcodes_df.at[idx, 'english_name'] = product_name_en
    
    clean_colums = ['product_name', 'english_name', "calories",	"protein",	"fat", "portion_size", "num_servings", 'matched_price', 'match_score', 'matched_receipt_name']
    cleaned_barcodes_df = barcodes_df[clean_colums]
    # Save the matched results
    cleaned_barcodes_df.to_csv(output_csv, index=False)
    print(f"\nSaved matched results to {output_csv}")
    
    # Print summary
    matched_count = barcodes_df['matched_price'].notna().sum()
    print(f"\nSummary: {matched_count}/{len(barcodes_df)} products matched")
    
    return cleaned_barcodes_df

def translate_name(item, src='es', dest='ca'):
    translator = Translator()
    try:
        translated = translator.translate(item, src=src, dest=dest)
        trans_item = translated.text
    except Exception:
        trans_item = item  # fallback
    return trans_item

if __name__ == '__main__':
    # Run the matching
    result_df = fuzzy_match_prices(threshold=60)
    
    if result_df is not None:
        print("\nMatched Products:")
        print(result_df[['product_name', 'matched_receipt_name', 'matched_price', 'match_score']].to_string())
