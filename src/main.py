import asyncio
import sys

from PyQt5.QtCore import QSize
from asyncqt import QEventLoop
from PyQt5.Qt import QApplication

from view.main_wizard import MainWizard

def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    desktop_size = app.desktop().size()
    desktop_size = None

    mainWindow = MainWizard(None, desktop_size=desktop_size)

    screenrect = app.primaryScreen().geometry()
    mainWindow.move(screenrect.left(), screenrect.top())
    mainWindow.showFullScreen()
    mainWindow.activateWindow()

    with loop:
        sys.exit(loop.run_forever())


if __name__ == "__main__":
    main()
