#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import os.path
import sys
import re
import tempfile

from sh import lxc_create, lxc_start, lxc_stop, lxc_destroy, lxc_list, lxc_clone, \
               lxc_backup, lxc_restore, lxc_execute, ssh, arp, ping

from deego.models import VirtualMachine
from deego.managers import VMManager

sys.stdout = os.fdopen(sys.stdout.fileno(), "wb", 0)

class LXCManager(VMManager):
    def __init__(self, *args, **kw):
        super(LXCManager, self).__init__(*args, **kw)
        self.bootstrap_name = 'bootstrap'
        self.lxc_root = '/var/lib/lxc'

        self.lxc_create = lxc_create.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.lxc_start = lxc_start.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.lxc_clone = lxc_clone.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.lxc_stop = lxc_stop.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.lxc_destroy = lxc_destroy.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.lxc_list = lxc_list.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.lxc_backup = lxc_backup.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.lxc_restore = lxc_restore.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
        self.lxc_execute = lxc_execute.bake(_tty_in=True, _tty_out=True, _err_to_out=True, _iter=True)
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

            for line in self.lxc_create(*arguments):
                self.out(line)

    def get_definition(self):
        lxc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lxc.conf'))

        with open(lxc_path, 'r') as lxc_conf:
            cpus = "-".join([mask for mask in self.vm.cpu_mask])
 
            return lxc_conf.read().format(
                name=self.vm.name,
                mac=self.vm.mac_address,
                cpu_mask=cpus,
                ram=self.vm.ram
            )

    def create(self):
        arguments = ['-t', 'ubuntu', '-n', self.vm.name]

        conf_path = os.path.join(tempfile.gettempdir().rstrip('/'), '{0}.conf'.format(self.vm.name))
        with open(conf_path, 'w') as lxc_conf:
            lxc_conf.write(self.get_definition())

        arguments.append('-f')
        arguments.append(conf_path)

        arguments.append('--fssize')
        arguments.append('{0}G'.format(self.vm.disk_size / 1024 / 1024))

        create_cmd = 'lxc-create {0}'.format(' '.join(arguments))
        self.cmd(create_cmd)

        for line in self.lxc_create(*arguments):
            self.out(line)

    def destroy(self):
        if self.vm.snapshotted:
            self.vm.revert()

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
        create_cmd = 'lxc-start -n {0} -d'.format(self.vm.name)
        self.cmd(create_cmd)
        for line in self.lxc_start('-n', self.vm.name, '-d'):
            self.out(line)

    def stop(self):
        create_cmd = 'lxc-stop -n {0}'.format(self.vm.name)
        self.cmd(create_cmd)
        for line in self.lxc_stop('-n', self.vm.name):
            self.out(line)

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
               "Connection to {0} closed.".format(self.vm.ip) not in message and \
               "[sudo] password for ubuntu:" not in message

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
        if self.vm.running:
            raise RuntimeError("You can't create a snapshot of a running VM. Call stop() first.")

        snapshot_cmd = 'lxc-backup {0} 1'.format(self.vm.name)
        self.cmd(snapshot_cmd)

        for line in self.lxc_backup(self.vm.name, 1):
            self.out(line)

        self.vm.snapshotted = True

    def revert(self):
        if self.vm.running:
            raise RuntimeError("You can't revert to a snapshot of a running VM. Call stop() first.")

        revert_cmd = 'lxc-restore {0} 0'.format(self.vm.name)
        self.cmd(revert_cmd)

        for line in self.lxc_restore(self.vm.name, 0):
            self.out(line)

