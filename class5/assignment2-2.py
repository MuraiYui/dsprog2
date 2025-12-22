import requests
import flet as ft

def main(page: ft.Page):
    page.title = "お天気予報アプリ"
    page.bgcolor = "#f0f2f5"  # 背景を少しグレーにしてカードを目立たせる
    page.padding = 0

    # --- ヘッダー（AppBar） ---
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.WB_SUNNY_OUTLINED),
        leading_width=40,
        title=ft.Text("天気予報", weight="bold"),
        center_title=False,
        bgcolor=ft.Colors.DEEP_PURPLE_700,
        color=ft.Colors.WHITE,
    )

    # 天気表示用のコンテナ
    weather_card_content = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    # カード型のデザイン
    weather_card = ft.Card(
        content=ft.Container(
            content=weather_card_content,
            padding=30,
            width=400,
        ),
        visible=False # 最初は隠しておく
    )

    def get_weather_icon(forecast_text):
        """天気の名前に合わせてアイコンと色を返す"""
        if "晴" in forecast_text:
            return ft.Icons.WB_SUNNY, ft.Colors.ORANGE
        elif "雨" in forecast_text:
            return ft.Icons.UMBRELLA, ft.Colors.BLUE
        elif "雪" in forecast_text:
            return ft.Icons.AC_UNIT, ft.Colors.LIGHT_BLUE
        else:
            return ft.Icons.CLOUD, ft.Colors.GREY_600

    def get_weather(code, name):
        try:
            url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{code}.json"
            data = requests.get(url).json()
            forecast = data[0]["timeSeries"][0]["areas"][0]["weathers"][0]
            
            # アイコンと色を判定
            icon_name, icon_color = get_weather_icon(forecast)

            # カードの中身を更新
            weather_card_content.controls = [
                ft.Text(f"{name}", size=24, weight="bold"),
                ft.Icon(name=icon_name, color=icon_color, size=100),
                ft.Text(forecast, size=18, text_align=ft.TextAlign.CENTER),
            ]
            weather_card.visible = True
            page.update()
        except Exception as ex:
            print(f"Error: {ex}")

    # --- 地域リストの作成 ---
    area_url = "https://www.jma.go.jp/bosai/common/const/area.json"
    area_data = requests.get(area_url).json()
    centers = area_data["centers"]
    offices = area_data["offices"]

    rail = ft.NavigationRail(
        extended=True,
        min_width=100,
        min_extended_width=200,
        selected_index=0,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.MAP, label="地域選択"),
            ft.NavigationRailDestination(icon=ft.Icons.SETTINGS, label="設定"),
        ],
    )

    lv = ft.ListView(expand=1, spacing=5)
    for c_code, c_info in centers.items():
        exp = ft.ExpansionTile(
            title=ft.Text(c_info["name"]),
            leading=ft.Icon(ft.Icons.LOCATION_ON_OUTLINED),
            controls=[
                ft.ListTile(
                    title=ft.Text(offices[o_code]["name"]),
                    on_click=lambda e, c=o_code, n=offices[o_code]["name"]: get_weather(c, n),
                ) for o_code in c_info["children"] if o_code in offices
            ]
        )
        lv.controls.append(exp)

    # 全体のレイアウト
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                ft.Container(content=lv, width=250),
                ft.VerticalDivider(width=1),
                ft.Container(
                    content=ft.Column(
                        [weather_card],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    expand=True,
                )
            ],
            expand=True
        )
    )

ft.app(target=main)