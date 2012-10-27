#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from os.path import exists
import re
import time

import libvirt
from sh import lxc_create, lxc_stop, lxc_destroy, lxc_list, lxc_clone, ssh, ping, arp

from deego.models import VirtualMachine

class VMManager(object):
    def __init__(self, ip_tries=60, sleep_time=0.5):
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

    def list(self):
        pass

    def get_ip(self):
        return None

    def wait(self):
        self.cmd('waiting for the vm to boot...')
        for ip_try in range(self.ip_tries):
            ip = self.get_ip()
            if ip is not None:
                self.vm.ip = ip
                self.cmd('vm booted and ready')
                return
            time.sleep(self.sleep_time)

        raise RuntimeError(
            'Machine {0} did not respond in a timely fashion after {1} seconds'.format(
                self.vm.name, self.ip_tries * self.sleep_time
            )
        )


class LXCManager(VMManager):
    def __init__(self, *args, **kw):
        super(LXCManager, self).__init__(*args, **kw)
        self.bootstrap_name = 'bootstrap'

        self.connection = libvirt.open("lxc:///")

        self.lxc_create = lxc_create.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.lxc_clone = lxc_clone.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.lxc_stop = lxc_stop.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.lxc_destroy = lxc_destroy.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.lxc_list = lxc_list.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.arp = arp.bake("-an", _tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)

    @classmethod
    def validate(self):
        return os.system('which lxc-create') != ''

    def bootstrap(self):
        self.cmd('bootstrapping lxc')
        if not 'bootstrap' in self.lxc_list():
            create_cmd = 'lxc-create -t ubuntu -n {0}'.format(self.bootstrap_name)
            self.cmd(create_cmd)
            arguments = ['-t', 'ubuntu', '-n', self.bootstrap_name]

            root_key_path = '/root/.ssh/id_rsa.pub'
            if exists(root_key_path):
                arguments.append('--')
                arguments.append('-S')
                arguments.append(root_key_path)

            for line in self.lxc_create(*arguments):
                self.out(line)

    def get_definition(self):
        xml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'libvirt.xml'))
        with open(xml_path, 'r') as xml:
            return xml.read() % {
                "name": self.vm.name,
                "mac": self.vm.mac_address
            }

    def create(self):
        create_cmd = 'lxc-clone -o {0} -n {1}'.format(self.bootstrap_name, self.vm.name)
        self.cmd(create_cmd)

        for line in self.lxc_clone(o=self.bootstrap_name, n=self.vm.name):
            self.out(line)

        self.domain = self.connection.defineXML(self.get_definition())
        self.domain.create()

    def destroy(self):
        try:
            self.domain = self.connection.lookupByName(self.vm.name)
        except:
            pass

        if hasattr(self, 'domain') and self.domain:
            self.cmd('Destroying domain...')
            self.domain.undefine()
            self.domain.destroy()

        if self.vm.name in self.lxc_list():
            create_cmd = 'lxc-destroy -f -n {0}'.format(self.vm.name)
            self.cmd(create_cmd)
            for line in self.lxc_destroy('-f', '-n', self.vm.name):
                self.out(line)

    def list(self):
        vms = []

        for vm in self.lxc_list():
            vm = vm.strip().lower()
            if vm and vm not in ('running', 'stopped', 'frozen', self.bootstrap_name):
                vms.append(VirtualMachine(self.__class__, name=vm))

        return vms

    def get_ip(self):
        ips = self.arp().split('\n')
        for ip in ips:
            if self.vm.mac_address in ip:
                match = re.match(r'.*\((?P<ip>(?:\d+[.]?)+)\).*', ip)
                if not match:
                    return None
                return match.groupdict()['ip']

    def start(self):
        pass

    def run_command(self, command):
        pass

class AutoVMManager(VMManager):
    managers = [LXCManager]

    def __init__(self, *args, **kw):
        super(AutoVMManager, self).__init__(*args, **kw)

        self.manager_instance = None
        for manager in self.managers:
            if manager.validate():
                self.manager_instance = manager(*args, **kw)

    def store_vm(self, vm):
        self.manager_instance.store_vm(vm)

    def bootstrap(self):
        return self.manager_instance.bootstrap()

    def create(self):
        return self.manager_instance.create()

    def start(self):
        return self.manager_instance.start()

    def destroy(self):
        return self.manager_instance.destroy()

    def list(self):
        return self.manager_instance.list()

    def run_command(self, command):
        return self.manager_instance.run_command(command)

    def wait(self):
        return self.manager_instance.wait()

    def get_ip(self):
        return self.manager_instance.get_ip()


