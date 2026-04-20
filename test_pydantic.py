from pydantic import BaseModel
import traceback
import sys

class ProductSaveRequest(BaseModel):
    name: str
    category_id: int = 0
    main_image: str
    images: list = []
    description: str = ""
    deposit: float = 0.0
    price: float = 0.0
    stock: int = 1
    sizes: list = []
    colors: list = []
    status: int = 1

payload = {
    'name': "123",
    'category_id': 0,
    'main_image': "http://example.com",
    'images': ["http://example.com"],
    'description': "",
    'deposit': 0,
    'price': 0,
    'stock': 1,
    'sizes': [],
    'colors': [],
    'status': 1
}

try:
    ProductSaveRequest(**payload)
    print("Pydantic parsed OK.")
except Exception as e:
    traceback.print_exc()
