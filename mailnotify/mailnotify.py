#!/usr/bin/env python3
import email
import os
import re

import bleach

import gi

gi.require_version("Notify", "0.7")
from gi.repository import Notify

from watchdog.events import FileSystemEventHandler

ICON_PATH = os.environ.get(
    "ICON_PATH",
    "/usr/share/icons/Yaru/48x48/apps/mail-app.png",
)


class MailWatchDaemon(FileSystemEventHandler):
    metadata_re = re.compile(r".*\.mbsyncstate\..*$")
    from_re = re.compile("(.*)<.*@.*>")

    def on_created(self, event):
        try:
            self._do_on_created(event)
        except Exception as e:
            print("ERROR", e)

    def _do_on_created(self, event):
        mail_path = event.src_path
        if self.metadata_re.match(mail_path):
            return

        if "INBOX" not in mail_path:
            return

        with open(mail_path) as f:
            message = email.message_from_file(f)

        from_address = message["From"]
        to_address = message["Delivered-To"]
        subject = message.get("Subject", "<NO SUBJECT>")

        message_content = []
        content_type = message.get_content_type()
        if content_type == "multipart/encrypted":
            message_content = ["<encrypted message>"]

        elif content_type == "multipart/alternative":
            for payload in message.get_payload():
                content_disposition = payload.get("Content-Disposition", "")
                if "attachment" in content_disposition:
                    continue

                if payload.get_content_type() == "text/plain":
                    payload_lines = (
                        payload.get_payload(decode=True)
                        .decode("utf-8")
                        .strip()[:100]
                        .split("\n")
                    )
                    message_content = [l for l in payload_lines if len(l) > 0][:3]
                    break

        elif content_type == "text/plain":
            message_content = message.get_payload()[:100].split("\n")[:3]

        if match := self.from_re.fullmatch(from_address):
            from_address = match.group(1)

        print(f"Recieved message from {from_address}")
        print(f"To {to_address}")
        print(f"With subject {subject}")

        notification = Notify.Notification.new(
            bleach.clean(from_address),
            bleach.clean(
                "\n".join(
                    [
                        f"<i>Subject: {subject}</i>",
                        f"<i>To: {to_address}</i>",
                    ]
                    + message_content
                ),
            ),
            ICON_PATH,
        )
        notification.set_timeout(15000)
        notification.show()
