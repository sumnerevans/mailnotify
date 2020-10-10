import time
from pathlib import Path

import gi

gi.require_version("Notify", "0.7")
from gi.repository import Notify

from watchdog.observers import Observer

from mailnotify.mailnotify import MailWatchDaemon

MAILDIR = Path("~/Mail").expanduser()

Notify.init("Mail Notification Daemon")


def main():
    daemon = MailWatchDaemon()
    observer = Observer()
    observer.schedule(daemon, str(MAILDIR.absolute()), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
    Notify.uninit()
