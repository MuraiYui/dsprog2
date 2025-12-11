import flet as ft


# --- ボタンの基底クラス ---
class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text


# --- 数字ボタンクラス ---
class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__(text, button_clicked, expand)
        self.bgcolor = ft.Colors.WHITE24
        self.color = ft.Colors.WHITE


# --- 演算子ボタンクラス (+, -, *, /) ---
class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        super().__init__(text, button_clicked)
        self.bgcolor = ft.Colors.ORANGE
        self.color = ft.Colors.WHITE


# --- 特殊アクションボタンクラス (AC, +/-, %) ---
class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        super().__init__(text, button_clicked)
        self.bgcolor = ft.Colors.BLUE_GREY_100
        self.color = ft.Colors.BLACK


# --- メインの電卓アプリケーションクラス ---
class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()

        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=40) 
        self.width = 350
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20
        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment="end"),
                # 1行目: AC, +/-, %, /
                ft.Row(
                    controls=[
                        ExtraActionButton(text="AC", button_clicked=self.button_clicked),
                        ExtraActionButton(text="+/-", button_clicked=self.button_clicked),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                # 2行目: 7, 8, 9, *
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                # 3行目: 4, 5, 6, -
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                # 4行目: 1, 2, 3, +
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                # 5行目: 0, ., =
                ft.Row(
                    controls=[
                        DigitButton(text="0", expand=2, button_clicked=self.button_clicked),
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ]
                ),
            ]
        )

    def button_clicked(self, e):
        data = e.control.data
        
        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.reset()
        
        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
            # ピリオドの重複チェック
            if data == "." and "." in self.result.value and not self.new_operand:
                pass
            # 新しいオペランドの入力開始
            elif self.result.value == "0" or self.new_operand == True:
                # 最初の入力が '.' の場合 '0.' にする
                self.result.value = "0." if data == "." and self.result.value == "0" else data
                self.new_operand = False
            # 数字の追加
            else:
                self.result.value = self.result.value + data

        elif data in ("+", "-", "*", "/"):
            # 連続して演算子を押した場合、前の演算を完了し、現在の演算子を設定
            if not self.new_operand:
                self.result.value = self.calculate(self.operand1, float(self.result.value), self.operator)
            
            self.operator = data
            
            if self.result.value == "Error":
                self.operand1 = 0.0
            else:
                self.operand1 = float(self.result.value)
            
            self.new_operand = True

        elif data in ("="):
            # 最終的な計算を実行
            self.result.value = self.calculate(self.operand1, float(self.result.value), self.operator)
            
            if self.result.value != "Error":
                self.operand1 = float(self.result.value) 
                self.new_operand = True
            
        elif data in ("%"):
            # パーセント計算
            current_value = float(self.result.value)
            self.result.value = self.format_number(current_value / 100)
            self.new_operand = True

        elif data in ("+/-"):
            # 符号反転
            current_value = float(self.result.value)
            if current_value != 0:
                self.result.value = self.format_number(-current_value)
            self.new_operand = False
        
        self.update()

    def format_number(self, num):
        # 小数点以下が0の場合は整数として表示
        if abs(num) % 1 == 0:
            return str(int(num))
        else:
            return str(num)

    def calculate(self, operand1, operand2, operator):
        # 計算ロジック
        if operator == "+":
            return self.format_number(operand1 + operand2)
        elif operator == "-":
            return self.format_number(operand1 - operand2)
        elif operator == "*":
            return self.format_number(operand1 * operand2)
        elif operator == "/":
            if operand2 == 0:
                return "Error"
            else:
                return self.format_number(operand1 / operand2)
        return self.format_number(operand2) 

    def reset(self):
        # 状態変数のリセット
        self.operator = "+"
        self.operand1 = 0.0
        self.new_operand = True


def main(page: ft.Page):
    page.title = "Simple Calculator"
    # デスクトップアプリとしてサイズを指定
    page.window_width = 370
    page.window_height = 550
    page.window_resizable = False 
    
    calc = CalculatorApp()
    page.add(calc)


# 🚨 .pyファイルでの標準的な起動方法
ft.app(main)