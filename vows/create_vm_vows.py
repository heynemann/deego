#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyvows import Vows, expect

from deego import VM, VirtualMachine, AutoVMManager

EXPECTED_IP = '192.168.122.17'
EXPECTED_COMMAND_RESULT = {
    'output':[
        { "message": 'echo "it works"', "message_type": "cmd"},
        { "message": "it works", "message_type": "out" }
    ],
    'status': 0
}

@Vows.batch
class CreateVMVows(Vows.Context):
    def setup(self):
        manager = AutoVMManager()
        for vm in manager.list():
            vm.destroy()

    def topic(self):
        return VM.create(
            cpus=2,
            ram=512, #MB
            disk_size=8000, #MB
            mac_address='52:54:00:4d:2b:cd'
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
                return vm.run_command('echo "it works"')

            def should_have_expected_result_from_command(self, topic):
                expect(topic).to_be_like(EXPECTED_COMMAND_RESULT)

        class AfterRunningTouch(Vows.Context):
            def topic(self, vm):
                vm.run_command('touch ~/test.txt')
                return vm

            class AndRestoringTheSnapshot(Vows.Context):
                def topic(self, vm):
                    vm.revert()
                    return vm

                class FileIsNotThere(Vows.Context):
                    def topic(self, vm):
                        return vm.run_command('ls ~/test.txt')

                    def should_have_status_code_not_zero(self, topic):
                        expect(topic['status']).not_to_equal(0)

