import sys
import os
import tkinter

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lib_path = os.path.join(base_path, 'lib')
if os.path.exists(lib_path):
    sys.path.append(lib_path)

from src.ui import ApplicationGUI

if __name__ == "__main__":
    root = tkinter.Tk()
    app = ApplicationGUI(root)
    root.mainloop()