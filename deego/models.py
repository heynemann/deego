#!/usr/bin/python
# -*- coding: utf-8 -*-

class VirtualMachine:
    def __init__(self, manager):
        self.manager = manager(self)
