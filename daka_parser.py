import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def fetch_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    return r.text

def parse_time(text):
    try:
        return datetime.strptime(text.strip(), "%H:%M:%S")
    except:
        return None

def get_today_cn_format():
    today = datetime.today()
    return f"{today.year}年{today.month}月{today.day}日"

def extract_hour_display(html, section_index=1):
    soup = BeautifulSoup(html, 'lxml')
    sections = soup.find_all("div", id="low-docs")
    if section_index >= len(sections):
        return "数据区块不存在"

    section = sections[section_index]
    lines = [p.get_text(strip=True) for p in section.find_all("p")]
    actual_hours = None
    expected_hours = None

    # 提取已打卡小时数
    for line in lines:
        if "已打卡" in line:
            match = re.search(r'已打卡([\d.]+)小时', line)
            if match:
                actual_hours = match.group(1)
                break 

    # 提取应打卡小时数
    for line in lines:     
        if "应打卡" in line:
            match = re.search(r'应打卡([\d.]+)小时', line)
            if match:
                expected_hours = match.group(1)
                break

    # 返回结果
    if actual_hours and expected_hours:
        return f"{actual_hours}h / {expected_hours}h"
    else:
        return None  # 返回 None 表示提取失败

def extract_checkin_status_from_section(html, section_index=3, target_date=None):
    if target_date is None:
        target_date = get_today_cn_format()

    soup = BeautifulSoup(html, 'lxml')
    sections = soup.find_all("div", id="low-docs")

    if section_index >= len(sections):
        print(f"section_index={section_index} 超出范围（共 {len(sections)} 个 section）")
        return [0, 0, 0, 0, 0, 0], {} 

    section = sections[section_index]
    p_tags = section.find_all("p")
    lines = [p.get_text(strip=True) for p in p_tags if p.get_text(strip=True)]

    # find lines for the target date 
    start_idx = -1 
    for i, line in enumerate(lines): 
        if target_date in line: 
            start_idx = i 
            break 
    if start_idx == -1: 
        return [0, 0, 0, 0, 0, 0], {}  # 返回默认值表示未找到目标日期
    
    # find lines for the target date 
    target_lines = lines[start_idx + 1: start_idx + 10]  # 10 行内提取数据

    periods = {
        "上午": {"签到": None, "签退": None},
        "下午": {"签到": None, "签退": None},
        "晚上": {"签到": None, "签退": None},
    }

    for line in target_lines:
        for period in periods:
            for action in periods[period]:
                key = f"{period}{action}"
                if key in line:
                    match = re.search(r"(\d{2}:\d{2}:\d{2})", line)
                    if match:
                        periods[period][action] = parse_time(match.group(1))

    result = []
    for period in ["上午", "下午", "晚上"]:
        checkin = periods[period]["签到"]
        checkout = periods[period]["签退"]
        result.append(1 if checkin else 0)
        if checkin and checkout:
            diff = (checkout - checkin).total_seconds() / 3600
            result.append(1 if diff >= 1 else 0)
        else:
            result.append(0)

    return result, periods  # 返回结果和时间段数据

# 示例使用
if __name__ == "__main__":
    url_s = {
        "lgr": "https://4096n4c151.xicp.fun/f/860e82a9814348d7a5ef/",
        "hsq": "https://4096n4c151.xicp.fun/f/48cda7c9209c4f1b8fc5/", 
        "lzy": "https://4096n4c151.xicp.fun/f/be375c34698f4bb48127/", 
        "hpy": "https://4096n4c151.xicp.fun/f/8e248cfbbcf375883e1e/"
    } 
    
    for name, url in url_s.items():
        html = fetch_html(url)
        print("-"*20, name, "-"*20)
        print("本月打卡小时数：", extract_hour_display(html))
        
        status, periods = extract_checkin_status_from_section(html)
        print(f"当日打卡状态：", status)
        # print periods data 
        for period in periods:
            for action in periods[period]:
                time_val = periods[period][action]
                time_str = time_val.strftime("%H:%M:%S") if time_val else "--:--:--"
                print(f"{period}{action}{time_str}")
    


