from pyzbar.pyzbar import decode
from PIL import Image
import json
 
 
def scan_qr_code(file):
        """
        Analyse un QR code pour en extraire les données.
        """
        img = Image.open(file)
        decoded_objects = decode(img)

        for obj in decoded_objects:
            print("Type:", obj.type)
            print("Data:", obj.data.decode('utf-8'))

        if decoded_objects:
            return decoded_objects[0].data.decode('utf-8')
        return None
        