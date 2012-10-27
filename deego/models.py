#!/usr/bin/python
# -*- coding: utf-8 -*-

from uuid import uuid4

from colorama import Fore, Style

class VirtualMachine:
    def __init__(self, manager, mac_address=None, name=None):
        self.ip = None
        self.name = name

        if not self.name or self.name is None:
            self.name = str(uuid4())

        self.mac_address = mac_address

        self.manager = manager()
        self.manager.store_vm(self)
        self.clear_messages()

    def clear_messages(self):
        self.messages = []

    def cmd(self, message):
        self.log(message, message_type='cmd')

    def out(self, message):
        self.log(message, message_type='out')

    def log(self, message, message_type):
        self.messages.append({
            'message': message,
            'type': message_type
        })

        color =''
        if message_type == 'cmd':
            color = Fore.YELLOW + Style.BRIGHT
        print "%s[%s] %s%s" % (color, message_type, message, Style.RESET_ALL)

    def bootstrap(self):
        self.manager.bootstrap()

    def start(self):
        self.manager.create()
        self.manager.start()
        self.manager.wait()

    def destroy(self):
        self.manager.destroy()

    def run_command(self, command):
        return self.manager.run_command(command)

