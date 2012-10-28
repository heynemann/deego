#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

class VMManager(object):
    def __init__(self, ip_tries=120, sleep_time=0.5):
        self.vm = None
        self.ip_tries = ip_tries
        self.sleep_time = sleep_time

    def store_vm(self, vm):
        self.vm = vm

    def cmd(self, msg):
        return self.vm.cmd(msg)

    def out(self, msg):
        return self.vm.out(msg)

    def bootstrap(self):
        pass

    def create(self):
        pass

    def start(self):
        pass

    def destroy(self):
        pass

    def run_command(self, command):
        pass

    def snapshot(self):
        pass

    def revert(self):
        pass

    def list(self):
        pass

    def get_ip(self):
        return None

    def ping(self):
        return None

    def set_cpu_count(self):
        pass

    def wait(self):
        self.cmd('waiting for vm network to show up...')
        for ip_try in range(self.ip_tries):
            ip = self.get_ip()
            if ip is not None:
                self.vm.ip = ip
                break
            time.sleep(self.sleep_time)

        if self.vm.ip is None:
            raise RuntimeError(
                'Machine {0} did not respond in a timely fashion after {1} seconds'.format(
                    self.vm.name, self.ip_tries * self.sleep_time
                )
            )

        self.cmd(
            "Machine {0}'s ip address found at {1}! waiting for vm to boot...".format(
                self.vm.name,
                self.vm.ip
            )
        )

        for ip_try in range(self.ip_tries):
            result = self.ping()
            if result:
                self.cmd('vm booted and ready')
                return
            time.sleep(self.sleep_time)

        raise RuntimeError(
            'Machine {0} did not respond in a timely fashion after {1} seconds'.format(
                self.vm.name, self.ip_tries * self.sleep_time
            )
        )


