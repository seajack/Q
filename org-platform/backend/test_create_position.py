import requests
import json

url = "http://localhost:8001/api/positions/"
data = {
    "name": "软件架构师",
    "code": "ARCHITECT",
    "department": 6,  # 技术部
    "management_level": "middle",
    "level": 8,  # 中层副职
    "description": "负责系统架构设计",
    "requirements": "8年以上架构设计经验",
    "responsibilities": "架构设计、技术选型、团队指导",
    "is_active": True
}

response = requests.post(url, json=data)
print("状态码:", response.status_code)
print("响应内容:", response.text)

if response.status_code == 201:
    print("职位创建成功!")
    position = response.json()
    print(f"职位ID: {position.get('id')}")
    print(f"职位名称: {position.get('name')}")
    print(f"管理层级: {position.get('management_level_display')}")
    print(f"职位级别: {position.get('level_display')}")
else:
    print("创建失败:")
    try:
        error_data = response.json()
        for field, errors in error_data.items():
            print(f"  {field}: {errors}")
    except:
        print("  无法解析错误信息")