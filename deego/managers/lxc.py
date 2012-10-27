#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from os.path import exists
import re

import libvirt
from sh import lxc_create, lxc_stop, lxc_destroy, lxc_list, lxc_clone, \
               lxc_backup, lxc_restore, ssh, arp, ping

from deego.models import VirtualMachine
from deego.managers import VMManager

sys.stdout = os.fdopen(sys.stdout.fileno(), "wb", 0)

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
        self.lxc_backup = lxc_backup.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.lxc_restore = lxc_restore.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.arp = arp.bake("-an", _tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.ping_cmd = ping.bake(_tty_in=True, _tty_out=True, _err_to_out=True)

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
        create_cmd = 'lxc-clone -o {0} -n {1} -s'.format(self.bootstrap_name, self.vm.name)
        self.cmd(create_cmd)

        for line in self.lxc_clone(o=self.bootstrap_name, n=self.vm.name, s=True):
            self.out(line)

        self.domain = self.connection.defineXML(self.get_definition())
        self.domain.create()

    def destroy(self):
        try:
            self.domain = self.connection.lookupByName(self.vm.name)
        except:
            pass

        if hasattr(self, 'domain') and self.domain:
            self.cmd('virsh destroy {0}'.format(self.vm.name))
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
                    continue
                return match.groupdict()['ip']
        return None

    def ping(self):
        try:
            self.ping_cmd("-c", "1", self.vm.ip)
            return True
        except:
            return False

    def start(self):
        pass

    def run_command(self, command, cwd=None):
        self.aggregated = ''
        self.last_output = ''
        self.vm.clear_messages()
        status_code = 0
        error = None

        self.cmd(command)

        if cwd is not None:
            command = 'cd {0} && {1}'.format(cwd, command)

        try:
            p = ssh('-t', '-o', 'UserKnownHostsFile=/dev/null', '-o',
                    'StrictHostKeyChecking=no', 'ubuntu@%s' % self.vm.ip, command,
                    _out=self.ssh_interact, _out_bufsize=0, _tty_in=True)
            p.wait()
        except Exception, err:
            status_code = 1
            error = err

        return {
            'status': status_code,
            'error': error,
            'output': self.vm.clear_messages()
        }

    def is_valid_message(self, message):
        return "Warning: Permanently added" not in message and \
               "Connection to {0} closed.".format(self.vm.ip) not in message

    def ssh_interact(self, char, stdin):

        self.aggregated += char

        if self.aggregated.endswith('password: ') or self.aggregated.endswith('password for ubuntu: '):
            stdin.put("ubuntu\n")

        if (char == '\n'):
            message = self.aggregated.replace(self.last_output, '')

            if self.is_valid_message(message):
                self.vm.out(message)

            self.last_output = self.aggregated

    def snapshot(self):
        snapshot_cmd = 'lxc-backup {0} 1'.format(self.vm.name)
        self.cmd(snapshot_cmd)

        for line in self.lxc_backup(self.vm.name, 1):
            self.out(line)

    def revert(self):
        revert_cmd = 'lxc-restore {0} 0'.format(self.vm.name)
        self.cmd(revert_cmd)

        for line in self.lxc_restore(self.vm.name, 0):
            self.out(line)

