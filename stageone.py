import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(total=2, backoff_factor=1)
session.mount("https://", HTTPAdapter(max_retries=retry_strategy))


def get_ability_info(ability_url):
    try:
        r = session.get(ability_url, timeout=(5, 30))
        r.raise_for_status()
        ab_data = r.json()
        for entry in ab_data.get("effect_entries", []):
            if entry["language"]["name"] == "en":
                return entry["short_effect"]
        return "无描述"
    except Exception as e:
        return f"error:{e}"


def fetch_one_pokemon(detail_poke_url):
    resp = session.get(detail_poke_url, timeout=(5, 30))
    resp.raise_for_status()
    d = resp.json()

    pokemon_info = {
        "name": d["name"],
        "height_m": round(d["height"] / 10, 2),
        "weight_kg": round(d["weight"] / 10, 2),
        "types": [t["type"]["name"] for t in d.get("types", [])],
        "abilities": []
    }

    for ab_item in d.get("abilities", []):
        ab_url = ab_item["ability"]["url"]
        ab_desc = get_ability_info(ab_url)
        pokemon_info["abilities"].append({
            "ability_name": ab_item["ability"]["name"],
            "is_hidden": ab_item["is_hidden"],
            "description": ab_desc
        })
        time.sleep(0.3)
    return pokemon_info


# ========== 分页配置 ==========
next_page_url = "https://pokeapi.co/api/v2/pokemon?limit=3"  # 一页3个
target_total = 8       # ✅总共只取8个就停止
collected = 0          # 已经拿到的计数

while next_page_url is not None:
    print(f"\n==== 请求分页：{next_page_url}")
    try:
        page_resp = session.get(next_page_url, timeout=(5,30))
        page_resp.raise_for_status()
        page_json = page_resp.json()
    except Exception as e:
        print("分页请求失败", e)
        break

    results = page_json.get("results", [])

    for item in results:
        if collected >= target_total:
            # 已经收集够8只，跳出for遍历本页的循环
            break

        print(f"\n正在处理：{item['name']} （第{collected+1}/{target_total}）")
        try:
            poke_result = fetch_one_pokemon(item["url"])
            print(f"名字:{poke_result['name']} | 身高:{poke_result['height_m']}m | 体重:{poke_result['weight_kg']}kg")
            print(f"属性: {poke_result['types']}")
            for ab in poke_result["abilities"]:
                hide_tag = "【隐藏】" if ab["is_hidden"] else ""
                print(f"  {hide_tag}{ab['ability_name']}: {ab['description']}")
            print("-" * 60)
        except Exception as err:
            print(f"处理失败 {item['name']} → {err}")

        collected += 1
        time.sleep(0.4)

    if collected >= target_total:
        # 凑够8个，直接跳出while分页大循环，不再请求next下一页
        break

    next_page_url = page_json["next"]


print(f"\n✅结束！一共获取 {collected} 只宝可梦，达到目标{target_total}只，停止分页。")
input("按回车退出")
