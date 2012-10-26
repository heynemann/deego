#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyvows import Vows, expect

from deego import VM, VirtualMachine, AutoVMManager

EXPECTED_IP = '10.10.10.10'
EXPECTED_COMMAND_RESULT = ['.', '..', 'a', 'b', 'c']

@Vows.batch
class CreateVMVows(Vows.Context):
    def topic(self):
        return VM.create(
            cpus=2,
            ram=512, #MB
            disk_size=8000, #MB
            mac_address="ff:ff:ff:ff:ff:00"
        )

    def should_be_vm(self, topic):
        expect(topic).to_be_instance_of(VirtualMachine)

    def should_have_auto_manager(self, topic):
        expect(topic.manager).to_be_instance_of(AutoVMManager)

    class ShouldStart(Vows.Context):
        def topic(self, vm):
            vm.start()
            return vm

        def should_have_expected_ip(self, topic):
            expect(topic.ip).to_equal(EXPECTED_IP)

        class CanRunCommand(Vows.Context):
            def topic(self, vm):
                return vm.run_command('ls /')

            def should_have_expected_result_from_command(self, topic):
                expect(topic).to_equal(EXPECTED_COMMAND_RESULT)

