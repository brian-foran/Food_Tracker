import re

class SmartReceiptParser:
    def __init__(self, receipt_text):
        
        self.receipt_text = receipt_text
        self.cleanup_receipt_text()
        self.receipt_list = self.receipt_text.split()


    def parse(self):
        # Extract prices using regex
        prices = self.extract_prices()
        #fix bad european decimal separator
        prices = [price.replace(',', '.') for price in prices]
        # Extract items using regex
        items = self.extract_items()
        
        return  dict(zip(items, prices))

    def cleanup_receipt_text(self):
        #add more cleaning steps as needed, for example removing newlines, tabs, etc.
        self.receipt_text = self.receipt_text.replace('.', ' ')
        return 

    def extract_prices(self):
        #prices = re.findall(r'\d+[,.]\d{0,2}', self.receipt_text)
        prices = re.findall(r'\d+[,.]\d{1,2}', self.receipt_text)
        return prices


    def extract_items(self):
        items = re.findall(r'[\S+ ]+', self.receipt_text)
        extracted_items = []
        for item in items:
            if any(char.isalpha() for char in item):
                #this is an item, but it needs to be cleaned
                item = item.strip().strip('0123456789.,').strip()
                extracted_items.append(item)
        return extracted_items
    
if __name__ == '__main__':
    # Example usage
    receipt_text = """1 LLET SEMI S/LACTOSA

1,62
1 DET. PELLS SENSIBLES

4,80
1 CLARA LÍQUIDA PASTEU

2,85
1 MINESTRA

1,83
1 BLAT DE MORO

1,24
2 F. RATLLAT S/LACTOSA
1,80
3,60
1 CREMA 100% CACAUET

2,85
1 PROTEINA 0% NAT

1,40
1 CAFÉ SOLUBLE CLASSIC

2,90
1 GUACAMOLE FRESC

1,80
1 CORIANDRE

1,25
1 SALMO AMB VERDURES

5,75
1 CONTRACUIXA S/PELL

3,25
1 PIT FAM.


TARGETA BANCARA
7,11
"""
    
    parser = SmartReceiptParser(receipt_text)
    print(parser.parse())
    #print(parser.receipt_list)
