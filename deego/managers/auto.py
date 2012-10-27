#!/usr/bin/python
# -*- coding: utf-8 -*-

from deego.managers import VMManager
from deego.managers.lxc import LXCManager

class AutoVMManager(VMManager):
    managers = [LXCManager]

    def __init__(self, *args, **kw):
        super(AutoVMManager, self).__init__(*args, **kw)

        self.manager_instance = None
        for manager in self.managers:
            if manager.validate():
                self.manager_instance = manager(*args, **kw)

    def __getattribute__(self, name):
        if name in ['manager_instance', 'managers']:
            return object.__getattribute__(self, name)

        return getattr(self.manager_instance, name)

