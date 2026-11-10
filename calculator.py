import ast
import ctypes
import re
import sys
import tkinter as tk
from tkinter import messagebox


def enable_windows_dpi_awareness():
    if sys.platform != "win32":
        return

    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except AttributeError:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except (AttributeError, OSError):
            ctypes.windll.user32.SetProcessDPIAware()


class ModernCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Emerald Calculator")
        self.root.geometry("390x700")
        self.root.minsize(350, 620)
        self.root.configure(bg="#101820")
        self.root.resizable(False, False)

        self.current_equation = ""
        self.last_expression = ""

        self.bg_color = "#101820"
        self.panel_color = "#1b2833"
        self.button_bg = "#243440"
        self.primary_green = "#20c997"
        self.dark_green = "#8ce3c7"
        self.text_color = "#f2f6f8"
        self.muted_color = "#91a4b2"
        self.accent_color = "#ff7b72"

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        header = tk.Frame(root, bg=self.bg_color)
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        tk.Label(
            header,
            text="EMERALD",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_color,
            fg=self.primary_green
        ).pack(side="left")
        tk.Label(
            header,
            text="CALCULATOR",
            font=("Segoe UI", 11),
            bg=self.bg_color,
            fg=self.muted_color
        ).pack(side="left", padx=(6, 0))

        display_panel = tk.Frame(root, bg=self.panel_color)
        display_panel.grid(row=1, column=0, sticky="ew", padx=16, pady=(8, 16))
        display_panel.grid_columnconfigure(0, weight=1)
        self.history_var = tk.StringVar(root)
        tk.Label(
            display_panel,
            textvariable=self.history_var,
            font=("Segoe UI", 12),
            bg=self.panel_color,
            fg=self.muted_color,
            anchor="e"
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 0))

        self.display_var = tk.StringVar(root)
        self.display = tk.Entry(
            display_panel,
            font=("Segoe UI", 34, "bold"),
            borderwidth=0,
            justify="right",
            bg=self.panel_color,
            fg=self.text_color,
            textvariable=self.display_var,
            state="readonly",
            readonlybackground=self.panel_color,
            insertwidth=0
        )
        self.display.grid(row=1, column=0, sticky="ew", padx=18, pady=(2, 16), ipady=8)
        self.update_display()

        keypad = tk.Frame(root, bg=self.bg_color)
        keypad.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 14))
        for column in range(4):
            keypad.grid_columnconfigure(column, weight=1, uniform="keypad")
        for row in range(6):
            keypad.grid_rowconfigure(row, weight=1, uniform="keypad")

        buttons = [
            ("AC", "C", 0, 0, "special"), ("(", "(", 0, 1, "function"),
            (")", ")", 0, 2, "function"), ("%", "%", 0, 3, "function"),
            ("7", "7", 1, 0, "num"), ("8", "8", 1, 1, "num"),
            ("9", "9", 1, 2, "num"), ("÷", "/", 1, 3, "op"),
            ("4", "4", 2, 0, "num"), ("5", "5", 2, 1, "num"),
            ("6", "6", 2, 2, "num"), ("×", "*", 2, 3, "op"),
            ("1", "1", 3, 0, "num"), ("2", "2", 3, 1, "num"),
            ("3", "3", 3, 2, "num"), ("−", "-", 3, 3, "op"),
            ("±", "±", 4, 0, "function"), ("0", "0", 4, 1, "num"),
            (".", ".", 4, 2, "num"), ("+", "+", 4, 3, "op"),
            ("⌫", "⌫", 5, 0, "special", 2), ("=", "=", 5, 2, "equal", 2)
        ]

        for item in buttons:
            text, key, row, col, button_type = item[:5]
            columnspan = item[5] if len(item) == 6 else 1
            btn_color, fg_color = self._button_colors(button_type)
            button = tk.Button(
                keypad,
                text=text,
                font=("Segoe UI", 16 if button_type == "num" else 14, "bold"),
                bg=btn_color,
                fg=fg_color,
                relief="flat",
                activebackground=self._hover_color(button_type),
                activeforeground=fg_color,
                bd=0,
                cursor="hand2",
                command=lambda value=key: self.click_event(value)
            )
            button.grid(
                row=row, column=col, columnspan=columnspan,
                padx=5, pady=5, sticky="nsew", ipady=4
            )
            button.bind(
                "<Enter>",
                lambda event, widget=button, kind=button_type:
                widget.config(bg=self._hover_color(kind))
            )
            button.bind(
                "<Leave>",
                lambda event, widget=button, kind=button_type:
                widget.config(bg=self._button_colors(kind)[0])
            )

        self.root.bind_all("<KeyPress>", self.handle_keypress)

    def _button_colors(self, button_type):
        if button_type == "op":
            return "#284b43", self.primary_green
        if button_type == "special":
            return "#49313a", self.accent_color
        if button_type == "equal":
            return self.primary_green, "#09251e"
        if button_type == "function":
            return "#2b3a46", self.text_color
        return self.button_bg, self.text_color

    def _hover_color(self, button_type):
        if button_type == "equal":
            return "#48d6aa"
        if button_type == "op":
            return "#356357"
        if button_type == "special":
            return "#60404a"
        return "#344956"

    def update_display(self):
        self.display_var.set(self.current_equation)

    def handle_keypress(self, event):
        keypad_keys = {
            "KP_0": "0", "KP_1": "1", "KP_2": "2", "KP_3": "3",
            "KP_4": "4", "KP_5": "5", "KP_6": "6", "KP_7": "7",
            "KP_8": "8", "KP_9": "9", "KP_Decimal": ".",
            "KP_Separator": ".",
            "KP_Add": "+", "KP_Subtract": "-", "KP_Multiply": "*",
            "KP_Divide": "/", "KP_Enter": "=",
            "KP_Insert": "0", "KP_End": "1", "KP_Down": "2",
            "KP_Next": "3", "KP_Left": "4", "KP_Begin": "5",
            "KP_Right": "6", "KP_Home": "7", "KP_Up": "8",
            "KP_Prior": "9", "KP_Delete": "."
        }

        key = keypad_keys.get(event.keysym)
        if key is None:
            if event.keysym in ("Return", "equal"):
                key = "="
            elif event.keysym == "BackSpace":
                key = "⌫"
            elif event.keysym == "Escape":
                key = "C"
            elif event.char and event.char in "0123456789.+-*/()%":
                key = event.char

        if key is not None:
            self.click_event(key)
            return "break"


    @staticmethod
    def _is_valid_expression(expression):
        if not expression or not expression.strip():
            return False

        expr = expression.strip()
        if not re.fullmatch(r"[0-9+\-*/().\s]+", expr):
            return False

        if expr.count("(") != expr.count(")"):
            return False

        balance = 0
        for ch in expr:
            if ch == "(":
                balance += 1
            elif ch == ")":
                balance -= 1
                if balance < 0:
                    return False

        if balance != 0:
            return False

        if expr.endswith(("+", "-", "*", "/")):
            return False

        try:
            tree = ast.parse(expr, mode="eval")
        except SyntaxError:
            return False

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                return False
            if isinstance(node, ast.Attribute):
                return False
            if isinstance(node, ast.Name):
                return False
            if isinstance(node, ast.Constant):
                if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                    return False
            if isinstance(node, ast.BinOp):
                if not isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.FloorDiv)):
                    return False
            if isinstance(node, ast.UnaryOp):
                if not isinstance(node.op, (ast.UAdd, ast.USub)):
                    return False

        return True

    @staticmethod
    def _last_number_fragment(expression):
        return re.split(r"[+\-*/()]", expression)[-1]

    def click_event(self, key):
        if key == "C":
            self.current_equation = ""
            self.history_var.set("")
            self.update_display()
            return

        if key == "⌫":
            self.current_equation = self.current_equation[:-1]
            self.update_display()
            return

        if key == "=":
            try:
                expr = self.current_equation.strip()
                if not expr or not self._is_valid_expression(expr):
                    raise ValueError("Geçersiz işlem!")

                sanitized = re.sub(r"[^0-9+\-*/().\s]", "", expr)
                sanitized = re.sub(r"\s+", "", sanitized)

                if not sanitized or sanitized[-1] in "+-*/":
                    raise ValueError("Geçersiz işlem!")

                result = eval(
                    compile(ast.parse(sanitized, mode="eval"), "<calculator>", "eval"),
                    {"__builtins__": None},
                    {}
                )

                if isinstance(result, float):
                    if result.is_integer():
                        res_str = str(int(result))
                    else:
                        res_str = format(result, ".12g")
                else:
                    res_str = str(result)

                self.history_var.set(f"{expr} =")
                self.current_equation = res_str
                self.update_display()
            except ZeroDivisionError:
                messagebox.showerror("Hata", "Sıfıra bölünme hatası!")
                self.current_equation = ""
                self.update_display()
            except Exception:
                messagebox.showerror("Hata", "Geçersiz işlem!")
                self.current_equation = ""
                self.update_display()
            return

        expr = self.current_equation
        last_char = expr[-1] if expr else ""

        if key == "%":
            number = re.search(r"(?:\d+(?:\.\d*)?|\.\d+)$", expr)
            if number is None:
                return
            value = float(number.group()) / 100
            replacement = format(value, ".12g")
            self.current_equation = expr[:number.start()] + replacement
            self.update_display()
            return

        if key == "±":
            number = re.search(r"(?:\d+(?:\.\d*)?|\.\d+)$", expr)
            if number is None:
                if not expr:
                    self.current_equation = "-"
                    self.update_display()
                return

            number_start = number.start()
            if number_start > 0 and expr[number_start - 1] == "-":
                prefix = expr[:number_start - 1]
                if not prefix or prefix[-1] in "+-*/(":
                    self.current_equation = prefix + expr[number_start:]
                else:
                    self.current_equation = expr[:number_start] + "-" + expr[number_start:]
            else:
                self.current_equation = expr[:number_start] + "-" + expr[number_start:]
            self.update_display()
            return

        if key == ".":
            fragment = self._last_number_fragment(expr)
            if "." in fragment:
                return
            if not expr or last_char in "+-*/(":
                self.current_equation += "0."
            else:
                self.current_equation += "."
            self.update_display()
            return

        if key in "+-*/":
            if not expr:
                if key == "-":
                    self.current_equation = "-"
                return
            if last_char in "+-*/(":
                if key == "-" and last_char != "-":
                    self.current_equation += "-"
                elif key == "-" and last_char == "(":
                    self.current_equation += "-"
                return
            if last_char == ")":
                self.current_equation += key
            else:
                self.current_equation += key
            self.update_display()
            return

        if key == "(":
            if expr and last_char not in "+-*/(":
                return
            self.current_equation += "("
            self.update_display()
            return

        if key == ")":
            if not expr or last_char in "+-*/(":
                return
            if expr.count("(") <= expr.count(")"):
                return
            self.current_equation += ")"
            self.update_display()
            return

        if expr and last_char in ")" and key.isdigit():
            self.current_equation += key
            self.update_display()
            return

        self.current_equation += str(key)
        self.update_display()


if __name__ == "__main__":
    enable_windows_dpi_awareness()
    root = tk.Tk()
    app = ModernCalculator(root)
    root.mainloop()
