from tkinter import *
from tkinter import ttk
from tkinter import font
from themes import *
from SmartButton import SmartButton


"""
TKINTER NICE DOCUMENTATION:
https://tkdocs.com/tutorial/firstexample.html
"""


class Calculator:

    def __init__(self, name: str):
        self.root = Tk()
        self.root.title(name)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=2)
        self.root.rowconfigure(2, weight=5)
        self.root.columnconfigure(0, weight=1)
        self.root.geometry('350x400+650+200')

        # global variables
        self.newinput = False
        self.division_error = False
        self.fontlist = fontlist
        self.font = StringVar()
        self.font.trace_add('write', self.set_font)
        self.theme = StringVar()
        self.theme.trace_add('write', self.apply_theme)

        # set default style
        self.style = ttk.Style()
        self.theme.set('matrix')
        self.apply_theme()
        # self.root.configure(background='#FEB7FF')
        # self.style.configure('TLabel', font=(self.font.get(), 20), background='#FEB7FF', foreground='#B5FFFE')
        # self.style.configure('TButton', font=(self.font.get(), 15), background='red', foreground='#B5FFFE')

        # dict with number buttons and corresponding position (tuples)
        self.numberslayout = {
            '7': (0,0), '8': (0,1), '9': (0,2),
            '4': (1,0), '5': (1,1), '6': (1,2),
            '1': (2,0), '2': (2,1), '3': (2,2),
                        '0': (3,1)
        }

        # dict with operations buttons and corresponding positions (tuples)
        self.operationslayout = {
            '+': (0,3),
            '-': (1,3),
            '*': (2,3),
            '/': (3,3),
        }

        self.set_menu()
        self.set_minidisplay()
        self.set_display()
        self.keyboard()

        self.root.mainloop()
    
    def set_menu(self):
        menubar = Menu(self.root)
        self.root.configure(menu=menubar)

        # options menu
        options_menu = Menu(menubar, tearoff=False)
        menubar.add_cascade(menu=options_menu, label='Options')

        # themes menu
        themes_menu = Menu(options_menu, tearoff=False)
        options_menu.add_cascade(menu=themes_menu, label='Themes')
        for theme in sorted(themes.keys()):
            themes_menu.add_radiobutton(label=theme, value=theme, variable=self.theme)

        # font menu
        font_menu = Menu(options_menu, tearoff=False)
        options_menu.add_cascade(menu=font_menu, label='Fonts')
        for fontname in sorted(self.fontlist):
            font_menu.add_radiobutton(label=fontname, value=fontname, variable=self.font)
    
    def set_minidisplay(self):
        labelframe = ttk.Frame(self.root)
        labelframe.grid(row=0, column=0, sticky='E', padx=25, pady=10)
        self.minidisplay = ttk.Label(labelframe)
        self.minidisplay.grid(row=0, column=0)

        # create minitext variable
        self.minitext = StringVar()
        self.minidisplay['textvariable'] = self.minitext

    def set_display(self):
        displayframe = ttk.Frame(self.root)
        displayframe.grid(row=1, column=0, sticky='E', padx=25, pady=10)
        self.display = ttk.Label(displayframe)
        self.display.grid(row=0, column=0)
        self.newinput = True

        # create global text variable which will be displayed and updated
        self.text = StringVar()
        self.display['textvariable'] = self.text

    def keyboard(self):
        kframe = ttk.Frame(self.root, padding=(3,3,3,3))
        kframe.grid(row=2, column=0, sticky='WENS', padx=10, pady=10)
        kframe.rowconfigure(list(range(4)), weight=1)
        kframe.columnconfigure(list(range(5)), weight=1)

        # put horizontal line
        separator = ttk.Separator(kframe, orient='horizontal')
        separator.place(y=-5, relwidth=1, relheight=1)

        # numbers
        for n, pos in self.numberslayout.items():
            SmartButton(kframe, lambda x = n: self.add_to_display(x), pos, text=n)

        # decimal
        SmartButton(kframe, self.make_decimal, (3,0), text='.')

        # negative
        SmartButton(kframe, self.negative, (3,2), text='(-)')

        # operations
        for symbol, pos in self.operationslayout.items():
            SmartButton(kframe, lambda x = symbol: self.operation(x), pos, text=symbol)

        # compute
        SmartButton(kframe, self.compute, (2,4), span=(2,1), text='=')

        # cancel
        SmartButton(kframe, self.ac, (0,4), text='AC')
        SmartButton(kframe, self.delete, (1,4), text='DEL')


    """
    Command functions
    """
    def add_to_display(self, char: str):
        if self.newinput:
            self.text.set('')
        current = self.text.get()
        self.text.set(current + char)
        self.newinput = False
    
    def make_decimal(self):
        current = self.text.get()
        itemlist = current.split(' ')
        if '.' not in itemlist[-1]:
            self.text.set(current + '.')
    
    def negative(self):
        current = self.text.get()
        if current == '':
            self.text.set('-')
    
    def operation(self, symbol: str):
        current = self.text.get()
        self.text.set(current + ' ' + symbol + ' ')
        self.newinput = False

    def ac(self):
        self.minitext.set('')
        self.text.set('')
    
    def delete(self):
        current = self.text.get()
        if current[-1].isnumeric():
            current = current[:-1]
        else:
            while not current[-1].isnumeric():
                current = current[:-1]
        self.text.set(current)

    """
    Functions to evaluate expression
    """
    def compute(self) -> None:
        expression = self.text.get()
        expression = expression.split(' ')
        expression = self.convert_to_float(expression)
        expression = self.multiply_divide(expression)
        if not self.division_error:
            result = self.add_subtract(expression)
            self.show_result(result)
        else:
            self.minitext.set('')
            self.text.set('error!')
        self.newinput = True
    
    def multiply_divide(self, expression: list) -> list:
        templist = []
        templist.append(expression[0])
        for i in range(int((len(expression) - 1)/2)):
            main = templist[-1]
            block = expression[1+2*i:3+2*i]  # takes every pair of two entries after the first element
            operand = block[0]
            number = block[1]
            if operand == '*':
                tempres = main * number
                templist[-1] = tempres
            elif operand == '/':
                if number != 0:
                    tempres = main / number
                    templist[-1] = tempres
                else:
                    self.division_error = True
                    pass
            else:
                templist.append(operand)
                templist.append(number)
        return templist
    
    def add_subtract(self, expression: list) -> float:
        result = expression[0]
        for i in range(int((len(expression) - 1)/2)):
            block = expression[1+2*i:3+2*i]  # takes every pair of two entries after the first element
            operand = block[0]
            number = block[1]
            if operand == '+':
                result += number
            elif operand == '-':
                result -= number
            else:
                continue
        return result
    
    def show_result(self, number: float):
        self.minitext.set(self.text.get() + ' ' + '=')  # update minidisplay
        if number.is_integer():
            self.text.set(int(number))
        else:
            self.text.set(round(number, 5))
    
    def convert_to_float(self, strlist) -> list:
        floatlist = []
        for x in strlist:
            try:
                floatlist.append(float(x))
            except:
                floatlist.append(x)
        return floatlist
    
    """
    Functions to evaluate errors
    """
    ###

    """
    Styling functions
    """
    def apply_theme(self, *args):
        t = self.theme.get()
        self.root.configure(background=themes[t]['basecolor'])
        self.style.configure('TLabel', font=(themes[t]['font'], 20), background=themes[t]['basecolor'], foreground=themes[t]['textcolor'])
        self.style.configure('TButton', font=(themes[t]['font'], 30), background=themes[t]['basecolor'], foreground=themes[t]['textcolor'])
    
    def set_font(self, *args):
        f = self.font.get()
        self.style.configure('TLabel', font=(f, 20))
        self.style.configure('TButton', font=(f, 30))


if __name__ == '__main__':
    Calculator('calculator')
    # for fontname in font.families():
    #     print(fontname)
