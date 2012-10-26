#!/usr/bin/python
# -*- coding: utf-8 -*-

import deego.managers as managers
import deego.models as models

class VM:
    @classmethod
    def create(cls, **kw):
        vm = models.VirtualMachine(
            manager = kw.get('manager', managers.AutoVMManager)
        )
        vm.bootstrap()
        return vm
