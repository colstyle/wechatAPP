import urllib.request
import json
import urllib.error

url = 'http://110.40.168.138:8000/api/v1/product/products'
data = {
    "name": "测试新增商品",
    "category_id": 1,
    "main_image": "http://example.com/test.png",
    "images": ["http://example.com/test.png"],
    "description": "测试",
    "deposit": 100,
    "price": 50,
    "stock": 1,
    "sizes": [],
    "colors": [],
    "status": 1
}

req = urllib.request.Request(
    url, 
    data=json.dumps(data).encode('utf-8'), 
    headers={'Content-Type': 'application/json', 'Authorization': 'admin_token_mock'}
)

try:
    response = urllib.request.urlopen(req)
    print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
except Exception as e:
    print(str(e))
