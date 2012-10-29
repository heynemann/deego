#!/usr/bin/python
# -*- coding: utf-8 -*-

from uuid import uuid4
import random

from colorama import Fore, Style

class VirtualMachine:
    def __init__(self, manager, cpu_mask=None, cpu_count=1, ram=512 * 1024, disk_size=8000 * 1024, name=None):
        self.messages = []
        self.clear_messages()

        self.ip = None
        self.cpu_count = cpu_count
        self.cpu_mask = cpu_mask
        self.ram = ram
        self.disk_size = disk_size

        self.name = name

        if not self.name or self.name is None:
            self.name = str(uuid4())

        mac = [0x00, 0x16, 0x3e,
        random.randint(0x00, 0x7f),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff)]
        self.mac_address = ':'.join(map(lambda x: "%02x" % x, mac))

        self.snapshotted = False

        self.manager = manager()
        self.manager.store_vm(self)

    def clear_messages(self):
        messages = self.messages
        self.messages = []
        return messages

    def cmd(self, message):
        self.log(message, message_type='cmd')

    def out(self, message):
        self.log(message, message_type='out')

    def log(self, message, message_type):
        self.messages.append({
            'message': message.strip(),
            'type': message_type
        })

        color =''
        if message_type == 'cmd':
            color = Fore.YELLOW + Style.BRIGHT
        print "%s[%s] %s%s" % (color, message_type, message, Style.RESET_ALL)

    def bootstrap(self):
        self.manager.bootstrap()

    def start(self):
        self.manager.start()
        self.manager.wait()
        self.manager.set_cpu_count()

    def create(self):
        self.manager.create()

    def destroy(self):
        self.manager.destroy()

    def run_command(self, command, cwd=None):
        return self.manager.run_command(command, cwd=cwd)

    def snapshot(self):
        return self.manager.snapshot()

    def revert(self):
        return self.manager.revert()
