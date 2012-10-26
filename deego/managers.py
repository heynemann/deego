#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from os.path import exists

import libvirt
from sh import lxc_create, lxc_stop, lxc_destroy, lxc_list, lxc_clone, ssh, ping, arp

class VMManager:
    def __init__(self, vm):
        self.vm = vm

    def cmd(self, msg):
        return self.vm.cmd(msg)

    def out(self, msg):
        return self.vm.out(msg)

    def bootstrap(self):
        pass

    def create(self, name):
        pass

    def start(self):
        pass

    def run_command(self, command):
        pass

class LXCManager(VMManager):
    def __init__(self, *args, **kw):
        VMManager.__init__(self, *args, **kw)
        self.bootstrap_name = 'bootstrap'

        self.lxc_create = lxc_create.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.lxc_clone = lxc_clone.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.lxc_stop = lxc_stop.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.lxc_destroy = lxc_destroy.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.lxc_list = lxc_list.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)

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

    def create(self, name):
        create_cmd = 'lxc-clone -o {0} -n {1}'.format(self.bootstrap_name, name)
        self.cmd(create_cmd)

        for line in self.lxc_clone(o=self.bootstrap_name, n=name):
            self.out(line)

    def destroy(self, name):
        create_cmd = 'lxc-destroy -f -n {0}'.format(name)
        self.cmd(create_cmd)
        for line in self.lxc_destroy('-f', '-n', name):
            self.out(line)



    def start(self):
        pass

    def run_command(self, command):
        pass

class AutoVMManager(VMManager):
    managers = [LXCManager]

    def __init__(self, *args, **kw):
        self.manager_instance = None
        for manager in self.managers:
            if manager.validate():
                self.manager_instance = manager(*args, **kw)

    def bootstrap(self):
        return self.manager_instance.bootstrap()

    def create(self, name):
        return self.manager_instance.create(name)

    def start(self):
        return self.manager_instance.start()

    def run_command(self, command):
        return self.manager_instance.run_command(command)


