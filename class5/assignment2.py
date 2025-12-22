import requests
import flet as ft

def main(page: ft.Page):
    page.title = "気象庁天気予報アプリ"
    
    # --- 表示用コンポーネント ---
    result_text = ft.Text("地域を選択してください", size=20, weight="bold")
    weather_detail = ft.Column()

    def get_weather(code, name):
        try:
            url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{code}.json"
            data = requests.get(url).json()
            weather_forecast = data[0]["timeSeries"][0]["areas"][0]["weathers"][0]
            
            result_text.value = f"【{name}】の天気"
            weather_detail.controls.clear()
            weather_detail.controls.append(ft.Text(weather_forecast, size=16))
            page.update()
        except Exception as ex:
            result_text.value = f"取得エラー: {ex}"
            page.update()

    # --- 地域データの取得 ---
    area_url = "https://www.jma.go.jp/bosai/common/const/area.json"
    area_data = requests.get(area_url).json()
    centers = area_data["centers"]
    offices = area_data["offices"]

    # --- UI: NavigationRail (修正済み：ft.Icons) ---
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.LOCATION_CITY, label="地域一覧"),
            ft.NavigationRailDestination(icon=ft.Icons.INFO_OUTLINE, label="アプリ情報"),
        ],
    )

    # --- UI: 地域リスト ---
    lv = ft.ListView(expand=1, spacing=5)
    for c_code, c_info in centers.items():
        exp = ft.ExpansionTile(
            title=ft.Text(c_info["name"]),
            controls=[
                ft.ListTile(
                    title=ft.Text(offices[o_code]["name"]),
                    data={"code": o_code, "name": offices[o_code]["name"]},
                    on_click=lambda e: get_weather(e.control.data["code"], e.control.data["name"]),
                ) for o_code in c_info["children"] if o_code in offices
            ]
        )
        lv.controls.append(exp)

    # --- レイアウト ---
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                ft.Container(content=lv, width=250),
                ft.VerticalDivider(width=1),
                ft.Container(
                    content=ft.Column([result_text, weather_detail], scroll=ft.ScrollMode.AUTO),
                    expand=True,
                    padding=20
                )
            ],
            expand=True
        )
    )

ft.app(target=main)