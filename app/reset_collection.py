"""컬렉션 초기화 스크립트."""

import requests

response = requests.post("http://localhost:8000/reset-collection")
print("응답 상태 코드:", response.status_code)
print("응답 내용:", response.json())

