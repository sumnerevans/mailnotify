#!/usr/bin/env python3
import email
import os
import re
from email.header import decode_header
from pathlib import Path

import gi

gi.require_version("Notify", "0.7")
from gi.repository import Notify

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

ICON_PATH = os.environ.get(
    "ICON_PATH",
    "/usr/share/icons/Yaru/48x48/apps/mail-app.png",
)

Notify.init("Mail Notification Daemon")


class MailWatchDaemon(FileSystemEventHandler):
    metadata_re = re.compile(r".*\.mbsyncstate\..*$")
    from_re = re.compile("(.*)<.*@.*>")

    def esc(self, string: str) -> str:
        return string.replace("<", "&lt;").replace(">", "&gt;")

    def on_created(self, event):
        try:
            self._do_on_created(event)
        except Exception as e:
            print("ERROR", e)

    def _get_header(self, message, header_name: str, default: str = "") -> str:
        header = decode_header(message.get(header_name, default))[0][0]
        return header.decode("utf-8") if isinstance(header, bytes) else header

    def _do_on_created(self, event):
        mail_path = event.src_path
        if self.metadata_re.match(mail_path):
            return

        if "INBOX" not in mail_path:
            return

        with open(mail_path) as f:
            message = email.message_from_file(f)

        from_address = self._get_header(message, "From")
        to_address = self._get_header(message, "Delivered-To")
        subject = self._get_header(message, "Subject", "<NO SUBJECT>")

        message_content = None
        for payload in message.get_payload():
            if isinstance(payload, email.message.Message):
                content_type = payload.get_content_type()
                content_disposition = payload.get("Content-Disposition", "")
                if "encrypted" in content_type:
                    message_content = ["<encrypted message>"]
                elif (content_type == "text/plain"
                      and "attachment" not in content_disposition):
                    payload_lines = (payload.get_payload(
                        decode=True).decode("utf-8").strip().split("\n"))
                    payload_lines = map(self.esc, payload_lines)
                    message_content = list(filter(len, payload_lines))[:3]

        if match := self.from_re.fullmatch(from_address):
            from_address = match.group(1)

        print(f"Recieved message from {from_address}")
        print(f"To {to_address}")
        print(f"With subject {subject}")

        notification = Notify.Notification.new(
            self.esc(from_address),
            "\n".join([
                f"<i>Subject: {self.esc(subject)}</i>",
                f"<i>To: {self.esc(to_address)}</i>",
                *message_content,
            ]),
            ICON_PATH,
        )
        notification.set_timeout(15000)
        notification.show()
