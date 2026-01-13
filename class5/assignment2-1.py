import requests
import flet as ft
import sqlite3
from datetime import datetime

# --- データベース操作 ---
def init_db():
    conn = sqlite3.connect("weather_app.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weather_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_code TEXT,
            area_name TEXT,
            forecast TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_weather_to_db(code, name, forecast):
    conn = sqlite3.connect("weather_app.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO weather_history (area_code, area_name, forecast) VALUES (?, ?, ?)",
        (code, name, forecast)
    )
    conn.commit()
    conn.close()

def get_history_by_date(date_str):
    conn = sqlite3.connect("weather_app.db")
    cur = conn.cursor()
    cur.execute(
        "SELECT area_name, forecast, created_at FROM weather_history WHERE date(created_at) = date(?) ORDER BY created_at DESC",
        (date_str,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

# --- メインアプリ ---
def main(page: ft.Page):
    init_db()
    page.title = "お天気予報アプリ (自動保存版)"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#f0f2f5"
    page.padding = 20

    result_title = ft.Text("地域を選択してください", size=20, weight="bold")
    weather_display = ft.Row(wrap=True, spacing=20)

    def get_icon(forecast):
        if "晴" in forecast: return ft.Icons.WB_SUNNY, ft.Colors.ORANGE
        if "雨" in forecast: return ft.Icons.UMBRELLA, ft.Colors.BLUE
        return ft.Icons.CLOUD, ft.Colors.GREY_600

    def display_results(results):
        weather_display.controls.clear()
        if not results:
            weather_display.controls.append(ft.Text("この日のデータはまだ保存されていません。地域を選択してデータを取得してください。"))
        else:
            for name, forecast, ts in results:
                ico, col = get_icon(forecast)
                weather_display.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(ts[:10], size=12, weight="bold", color="blue700"),
                                ft.Icon(ico, color=col, size=50),
                                ft.Text(name, size=16, weight="bold"),
                                ft.Text(forecast, size=14, text_align=ft.TextAlign.CENTER),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                            padding=20, width=170,
                        )
                    )
                )
        page.update()

    # 最新情報を取得してDBに保存する共通関数
    def fetch_latest_and_save(code, name):
        try:
            url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{code}.json"
            res = requests.get(url).json()
            forecast = res[0]["timeSeries"][0]["areas"][0]["weathers"][0]
            save_weather_to_db(code, name, forecast)
            return forecast
        except:
            return None

    def fetch_and_display(code, name):
        forecast = fetch_latest_and_save(code, name)
        if forecast:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            display_results([(name, forecast, now_str)])
            result_title.value = f"【{name}】の最新予報を表示・保存しました"
        else:
            result_title.value = "データ取得エラー"
        page.update()

    # --- カレンダー変更時の処理 ---
    def on_date_change(e):
        if date_picker.value:
            picked_date = date_picker.value.strftime("%Y-%m-%d")
            result_title.value = f"{picked_date} の保存済み履歴"
            history = get_history_by_date(picked_date)
            
            # ここが重要：もし今日の日付を選んでデータがなければ、全地域の最新をDBに貯めるヒントを出す
            display_results(history)

    date_picker = ft.DatePicker(
        on_change=on_date_change,
        first_date=datetime(2023, 1, 1),
        last_date=datetime(2026, 12, 31),
    )
    page.overlay.append(date_picker)

    # 地域リスト
    area_data = requests.get("https://www.jma.go.jp/bosai/common/const/area.json").json()
    lv = ft.ListView(expand=1, spacing=5)
    for c_code, c_info in area_data["centers"].items():
        exp = ft.ExpansionTile(
            title=ft.Row([ft.Icon(ft.Icons.MAP), ft.Text(c_info["name"])]),
            controls=[
                ft.ListTile(
                    title=ft.Text(area_data["offices"][o]["name"]),
                    subtitle=ft.Text(f"Code: {o}"),
                    on_click=lambda e, c=o, n=area_data["offices"][o]["name"]: fetch_and_display(c, n)
                ) for o in c_info["children"] if o in area_data["offices"]
            ]
        )
        lv.controls.append(exp)

    page.add(
        ft.Row(
            [
                ft.Column([
                    ft.Text(" 地域を選択", size=16, weight="bold"),
                    ft.Container(lv, width=280, expand=True, bgcolor=ft.Colors.WHITE, border_radius=15, padding=10),
                ]),
                ft.VerticalDivider(width=1),
                ft.Column(
                    [
                        ft.Row([
                            result_title,
                            ft.IconButton(
                                icon=ft.Icons.CALENDAR_MONTH,
                                on_click=lambda _: setattr(date_picker, "open", True) or page.update(),
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Divider(),
                        ft.Column([weather_display], scroll=ft.ScrollMode.AUTO, expand=True)
                    ],
                    expand=True,
                )
            ],
            expand=True
        )
    )
    page.update()

ft.app(target=main)