import flet as ft
import math  # ★ 科学計算のために math モジュールをインポート


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


# --- 特殊アクションボタンクラス (AC, +/-, %, sin, ln, etc.) ---
class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__(text, button_clicked, expand)
        self.bgcolor = ft.Colors.BLUE_GREY_100
        self.color = ft.Colors.BLACK


# --- メインの電卓アプリケーションクラス ---
class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()

        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=40) 
        self.width = 450 # 幅を広げ、科学計算ボタンを配置
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20
        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment="end"),
                
                # ★ 科学計算モードのボタン行 (新規追加)
                ft.Row(
                    controls=[
                        ExtraActionButton(text="sin", button_clicked=self.button_clicked),
                        ExtraActionButton(text="cos", button_clicked=self.button_clicked),
                        ExtraActionButton(text="tan", button_clicked=self.button_clicked),
                        ExtraActionButton(text="ln", button_clicked=self.button_clicked),
                        ExtraActionButton(text="log10", button_clicked=self.button_clicked),
                        ExtraActionButton(text="sqrt", button_clicked=self.button_clicked),
                        ExtraActionButton(text="x^y", button_clicked=self.button_clicked),
                    ],
                ),

                # 既存のボタン行 (AC, +/-, %, /)
                ft.Row(
                    controls=[
                        ExtraActionButton(text="AC", button_clicked=self.button_clicked),
                        ExtraActionButton(text="+/-", button_clicked=self.button_clicked),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                
                # 7, 8, 9, *
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                
                # 4, 5, 6, -
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                
                # 1, 2, 3, +
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                
                # 0, ., =
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
        
        # 1. エラーリセット / AC
        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.reset()
            self.update()
            return
        
        # 2. 単項科学計算オペレーション (sin, cos, tan, ln, log10, sqrt)
        elif data in ("sin", "cos", "tan", "ln", "log10", "sqrt"):
            try:
                current_value = float(self.result.value)
                result = current_value
                
                if data == "sin":
                    result = math.sin(current_value) # ラジアンで計算
                elif data == "cos":
                    result = math.cos(current_value) # ラジアンで計算
                elif data == "tan":
                    result = math.tan(current_value) # ラジアンで計算
                elif data == "ln":
                    result = math.log(current_value) # 自然対数 (底 e)
                elif data == "log10":
                    result = math.log10(current_value) # 常用対数 (底 10)
                elif data == "sqrt":
                    if current_value < 0:
                        raise ValueError("負の数の平方根")
                    result = math.sqrt(current_value) # 平方根

                self.result.value = self.format_number(result)
                self.new_operand = True
            
            except ValueError:
                self.result.value = "Error"
                self.reset()
            
        # 3. 数字/ドットの入力
        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
            if data == "." and "." in self.result.value and not self.new_operand:
                pass
            elif self.result.value == "0" or self.new_operand == True:
                self.result.value = "0." if data == "." and self.result.value == "0" else data
                self.new_operand = False
            else:
                self.result.value = self.result.value + data

        # 4. 二項演算子 (+, -, *, /, x^y)
        elif data in ("+", "-", "*", "/", "x^y"):
            # 既存の計算がある場合、先に計算を完了
            if not self.new_operand:
                self.result.value = self.calculate(self.operand1, float(self.result.value), self.operator)
            
            self.operator = data
            
            if self.result.value == "Error":
                self.operand1 = 0.0
            else:
                self.operand1 = float(self.result.value)
            
            self.new_operand = True

        # 5. イコール
        elif data == "=":
            # 最終的な計算を実行
            self.result.value = self.calculate(self.operand1, float(self.result.value), self.operator)
            
            if self.result.value != "Error":
                self.operand1 = float(self.result.value) 
                self.new_operand = True
            
        # 6. パーセント
        elif data == "%":
            current_value = float(self.result.value)
            self.result.value = self.format_number(current_value / 100)
            self.new_operand = True

        # 7. 符号反転
        elif data == "+/-":
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
        try:
            if operator == "+":
                return self.format_number(operand1 + operand2)
            elif operator == "-":
                return self.format_number(operand1 - operand2)
            elif operator == "*":
                return self.format_number(operand1 * operand2)
            elif operator == "/":
                if operand2 == 0:
                    return "Error"
                return self.format_number(operand1 / operand2)
            elif operator == "x^y":  # ★ べき乗計算
                return self.format_number(math.pow(operand1, operand2))
            
            return self.format_number(operand2) 
        except ValueError:
            return "Error"

    def reset(self):
        # 状態変数のリセット
        self.operator = "+"
        self.operand1 = 0.0
        self.new_operand = True


def main(page: ft.Page):
    page.title = "Scientific Calculator"
    # ウィンドウの幅と高さを科学計算モードに合わせて調整
    page.window_width = 470
    page.window_height = 650
    page.window_resizable = False 
    
    calc = CalculatorApp()
    page.add(calc)


# 起動
ft.app(main)