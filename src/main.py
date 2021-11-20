import asyncio
import sys

from asyncqt import QEventLoop
from globals import USERS
from PyQt5.Qt import QApplication
from view.main_wizard import MainWizard


def main():
    if len(USERS) != 2:
        raise ValueError("Only 2 Users are able to use this app currently. Size of users has to be 2!")

    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    desktop_size = app.desktop().size()
    desktop_size = None

    mainWindow = MainWizard(None, desktop_size=desktop_size, users=USERS)

    screenrect = app.primaryScreen().geometry()
    mainWindow.move(screenrect.left(), screenrect.top())
    mainWindow.showFullScreen()
    mainWindow.activateWindow()

    with loop:
        sys.exit(loop.run_forever())


if __name__ == "__main__":
    main()
