from PIL import Image
from pyzbar.pyzbar import decode, ZBarSymbol

img = Image.open('img/image.jpg')

decoded_list = decode(img)

print(type(decoded_list))
# <class 'list'>

print(len(decoded_list))
# 3

print(type(decoded_list[0]))
# <class 'pyzbar.pyzbar.Decoded'>

for d in decoded_list:
    print(d.data.decode("utf-8"))
    