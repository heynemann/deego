#!/usr/bin/python
# -*- coding: utf-8 -*-

from deego.core import VM
from deego.models import VirtualMachine
from deego.managers import VMManager

try:
    from deego.managers.auto import AutoVMManager
except ImportError:
    pass

try:
    from deego.managers.lxc import LXCManager
except ImportError:
    pass
