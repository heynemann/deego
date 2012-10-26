#!/usr/bin/python
# -*- coding: utf-8 -*-

from uuid import uuid4

from colorama import Fore, Style

class VirtualMachine:
    def __init__(self, manager):
        self.manager = manager(self)
        self.ip = None
        self.messages = []
        self.name = str(uuid4())

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
        self.manager.create(self.name)
        self.manager.start()

    def run_command(self, command):
        self.manager.run_command(command)
