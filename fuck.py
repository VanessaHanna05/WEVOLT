import qrcode

url = "http://192.168.248.22:8501/"
img = qrcode.make(url)
img.save("streamlit_qr.png")

import os

print("Saving to:", os.getcwd())
img.save("streamlit_qr.png")