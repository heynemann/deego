#!/usr/bin/python
# -*- coding: utf-8 -*-

import deego.managers as managers
import deego.models as models

class VM:
    @classmethod
    def create(cls, **kw):
        if not 'mac_address' in kw:
            raise ValueError("The mac address for the machine is required to create it")

        vm = models.VirtualMachine(
            manager = kw.get('manager', managers.auto.AutoVMManager),
            mac_address = kw['mac_address']
        )
        vm.bootstrap()
        return vm
