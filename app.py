from flask import Flask, render_template
from daka_parser import fetch_html, extract_hour_display, extract_checkin_status_from_section

app = Flask(__name__)

@app.route("/")
def home():
    url_s = {
        "lgr": "https://4096n4c151.xicp.fun/f/860e82a9814348d7a5ef/",
        "hsq": "https://4096n4c151.xicp.fun/f/48cda7c9209c4f1b8fc5/", 
        "lzy": "https://4096n4c151.xicp.fun/f/be375c34698f4bb48127/", 
        "hpy": "https://4096n4c151.xicp.fun/f/8e248cfbbcf375883e1e/"
    } 

    user_data = [] 
    for name, url in url_s.items(): 
        try: 
            html = fetch_html(url)
            hour_summary = extract_hour_display(html)
            status, periods = extract_checkin_status_from_section(html)
            
            # 将 periods 转换为字符串格式
            periods_str = {} 
            for period in periods:
                periods_str[period] = {}
                for action in periods[period]:
                    time_val = periods[period][action]
                    time_str = time_val.strftime("%H:%M:%S") if time_val else "--:--:--"
                    periods_str[period][action] = time_str
            
            user_data.append({
                "name": name, 
                "hour": hour_summary, 
                "status": status,
                "periods": periods_str
            })
        except Exception as e: 
            user_data.append({
                "name": name, 
                "hour": "获取失败", 
                "status": [0, 0, 0, 0, 0, 0],
                "periods": {
                    "上午": {"签到": "--:--:--", "签退": "--:--:--"},
                    "下午": {"签到": "--:--:--", "签退": "--:--:--"},
                    "晚上": {"签到": "--:--:--", "签退": "--:--:--"},
                }
            })

    return render_template("index.html", users=user_data)

if __name__ == "__main__":
    app.run(debug=True)
