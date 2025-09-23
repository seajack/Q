import requests
import json

url = "http://localhost:8001/api/employees/"
data = {
    "name": "张三",
    "employee_id": "EMP001", 
    "gender": "M",
    "phone": "13800138000",
    "email": "zhangsan@company.com",
    "department": 6,
    "position": 4,
    "hire_date": "2023-01-01",
    "status": "active",
    "username": "zhangsan"
}

response = requests.post(url, json=data)
print("状态码:", response.status_code)
print("响应内容:", response.text)

if response.status_code == 201:
    print("员工创建成功!")
    employee = response.json()
    print(f"员工ID: {employee.get('id')}")
    print(f"员工姓名: {employee.get('name')}")
else:
    print("创建失败:")
    try:
        error_data = response.json()
        for field, errors in error_data.items():
            print(f"  {field}: {errors}")
    except:
        print("  无法解析错误信息")