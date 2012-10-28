#!/usr/bin/python
# -*- coding: utf-8 -*-

import deego.managers as managers
import deego.models as models

MB = 1024

class VM:
    @classmethod
    def create(cls, **kw):
        ram = int(kw.get('ram', 512)) * MB
        cpu_count = int(kw.get('cpu_count', 1))
        cpu_mask = kw.get('cpu_mask', None)
        disk_size = int(kw.get('disk_size', 8 * MB)) * MB
        manager = kw.get('manager', managers.auto.AutoVMManager)

        vm = models.VirtualMachine(
            cpu_count=cpu_count,
            cpu_mask=cpu_mask,
            ram=ram,
            disk_size=disk_size,
            manager=manager
        )
        vm.bootstrap()
        vm.create()
        return vm
