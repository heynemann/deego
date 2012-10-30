#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyvows import Vows, expect

from deego import VM, VirtualMachine, AutoVMManager

EXPECTED_IP = '192.168.122'
EXPECTED_COMMAND_RESULT = { "message": 'it works', "type": "out"}

@Vows.batch
class CreateVMVows(Vows.Context):
    def setup(self):
        manager = AutoVMManager()
        for vm in manager.list():
            vm.destroy()

    def topic(self):
        return VM.create(
            cpu_mask="01",
            ram=512, #MB
            disk_size=8000 #MB
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
            expect(topic.ip).not_to_be_null()

        class CanRunCommand(Vows.Context):
            def topic(self, vm):
                return vm.run_command('echo "it works"')

            def should_have_expected_status_code(self, topic):
                expect(topic['status']).to_equal(0)

            def should_have_expected_result_from_command(self, topic):
                expect(topic['output']).to_include(EXPECTED_COMMAND_RESULT)

        #class HasProperNumberOfCPUs(Vows.Context):
            #def topic(self, vm):
                #return vm.run_command('cat /proc/cpuinfo | grep processor | wc -l')

            #def should_have_two_cpus(self, topic):
                #expect(topic['output']).to_include({'message': u'2', 'type': 'out'})

        class WhenSnapshottedAndReverted(Vows.Context):
            def topic(self, vm):
                import ipdb;ipdb.set_trace()
                vm.stop()
                vm.snapshot()
                vm.start()
                vm.run_command('echo "test" > ~/test.txt')
                vm.stop()
                vm.revert()
                vm.start()
                return vm

            class FileIsNotThere(Vows.Context):
                def topic(self, vm):
                    result = vm.run_command('cat ~/test.txt')
                    return result

                def should_have_status_code_not_zero(self, topic):
                    expect(topic['status']).not_to_equal(0)

