from PyQt5.QtWidgets import QApplication
from PyWeChatSpy.ui.ui import SpyUI
import sys


if __name__ == '__main__':
    app = QApplication(sys.argv)
    spy_ui = SpyUI()
    sys.exit(app.exec_())