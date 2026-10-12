import requests
import json


url = "https://api.github.com/repos/langchain-ai/langchain"


# 获取 GitHub 数据
response = requests.get(url)

data = response.json()


# 显示在屏幕
print("项目名称:")
print(data["name"])

print("Star 数量:")
print(data["stargazers_count"])


# 写入文件
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(
        data,
        f,
        ensure_ascii=False,
        indent=2
    )


print("数据已经保存到 data.json")