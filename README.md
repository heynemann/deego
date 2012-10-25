![deego](https://raw.github.com/heynemann/deego/master/logo.png) 

# What is deego?

* deego is a vm manager for dummies (like me);
* deego is for those that feel threatened every time they need a VM;
* deego is for those that want virtualization to be easy (as it should);
* deego is all it can be and more (ok pushed a little here).

## How do I create a VM?

A line of code is worth, well, the number of characters you need to type. So
let's get to it.

    from deego import VM

    def main():
        vm = VM.create(
            cpus=2,
            ram=512, #MB
            disk_size=8000, #MB
            mac_address="ff:ff:ff:ff:ff:00"
        )
        vm.start() # this will block until VM booted
        print vm.ip
        print vm.run_command('ls /')

Man, this is kinda embarassing. I wanted to show more, but that's pretty much
all I got.

## What will deego use under the hood?

Glad you asked, since it's so freaking awesome cool stuff: libvirt. Yeah, I
wanted to say more, but once again it's that simple.

deego will always try to select the best possible way to create the VM in your
environment.

We'll try to create VMs using the providers in this order:

* linux containers (LXCManager);
* kvm (KVMManager);
* vmware (VMWareManager);
* virtual box (VBoxManager).

Please note that you can easily pass them to the VM class if you want a
specific one:

    from deego import VM, KVMManager

    def main():
        vm = VM.create(
            cpus=2,
            ram=512,
            disk_size=8000,
            mac_address="ff:ff:ff:ff:ff:00",
            manager=KVMManager
        )
        vm.start() # this will block until VM booted
        print vm.ip
        print vm.run_command('ls /')

## What OS does deego install VMs with?

Ubuntu server. We'll always try to use the latest stable version of ubuntu, so
you don't have to worry about it.

## How does deego provision my VM?

The easiest way of provisioning a VM: not doing it. Provisioning is entirely
left as an exercise to the reader.

## I want to contribute! How to do it?

Fork, Code, Pull Request, Rinse, Repeat.
