import virtualbox as vb
import time
import subprocess


services = {
    1: "CREATE_VM",
    2: "DELETE_VM"
}
CLUSTER_MAX_SIZE = 7
CLUSTER_MIN_SIZE = 3


class VBManager:
    def __init__(self):
        self.services = services
        self.vbox = vb.VirtualBox()
        self.cold_vm_snapshot = 'scaling'

    def list_all(self):
        return {'rst': 'success', 'data': self.services}

    def create_config_VM(self):
        isHotVM = False
        for vm in self.vbox.machines:
            if vm.state == 1 and vm.name != 'namenode':
                # start an existed and power-offed VM.
                print('Starting VM %s ...' % vm.name)
                try:
                    subprocess.check_call("vboxmanage startvm {} --type headless".format(vm.name).split(), \
                                   stdout=subprocess.PIPE)
                except subprocess.CalledProcessError:
                    print('Hot VM creation failed!')
                    return {'rst': 'fail'}
                isHotVM = True
                bootup_vm = vm.name
                break
        if not isHotVM:
            if self.vbox.machines.__len__() >= CLUSTER_MAX_SIZE:
                print('Cold VM creation failed: Beyond the cluster size limitation.')
                return {'rst': 'fail'}
            # create a new VM by cloning.
            datanode_num = str(self.vbox.machines.__len__())
            new_vm_name = 'data' + datanode_num
            print('Cloning a VM %s ...' % new_vm_name)
            try:
                subprocess.check_call(
                    "vboxmanage clonevm data1 --snapshot {} --name {} --register"\
                        .format(self.cold_vm_snapshot, new_vm_name).split(), \
                    stdout=subprocess.PIPE)
            except subprocess.CalledProcessError:
                print('Cold VM creation failed: Clone VM error.')
                return {'rst': 'fail'}
            print('Starting a VM %s ...' % new_vm_name)
            try:
                subprocess.check_call("vboxmanage startvm {} --type headless".format(new_vm_name).split(), \
                                                  stdout=subprocess.PIPE)
            except subprocess.CalledProcessError:
                print('Cold VM creation failed: Start VM error.')
                return {'rst': 'fail'}
            # config VM
            vm = self.vbox.find_machine(new_vm_name)
            time.sleep(15)
            timeout = 15
            while vm.state != 5:
                if timeout > 0:
                    time.sleep(5)
                    timeout -= 5
                else:
                    print('VM creation failed: Timeout.')
                    return {'rst': 'fail'}
            print('Configuring a VM %s ...' % new_vm_name)
            with vm.create_session() as session:
                time.sleep(15)
                with session.console.guest.create_session('storm', '14641') as gs:
                    time.sleep(15)
                    _, o, e = gs.execute('/usr/bin/sudo', ['/home/storm/lab/config_VM.py', ('%s' % datanode_num)])
                    print('config output: ' + str(o))
                    print('config error: ' + str(e))
            time.sleep(15)
            print('Restarting a VM %s ...' % new_vm_name)
            try:
                subprocess.check_call("vboxmanage controlvm {} reset".format(new_vm_name).split(), \
                                      stdout=subprocess.PIPE)
            except subprocess.CalledProcessError:
                print('Cold VM creation failed: Reset VM error.')
                return {'rst': 'fail'}
            bootup_vm = new_vm_name
        # check if VM is running.
        vm = self.vbox.find_machine(bootup_vm)
        time.sleep(20)
        timeout = 10
        while vm.state != 5:
            if timeout > 0:
                time.sleep(5)
                timeout -= 5
            else:
                print('VM creation failed: Timeout.')
                return {'rst': 'fail'}
        return {'rst': 'success'}

    def shrink_VM(self):
        if len(self.vbox.machines) <= CLUSTER_MIN_SIZE:
            print('VM shinkage failed: Beyond the cluster size limitation.')
            return {'rst': 'fail'}
        for vm in self.vbox.machines:
            if vm.state == 5 and vm.name not in ['namenode', 'data1', 'data2']:
                # shutdown an existed and running VM.
                print('Shutdowning a VM %s ...' % vm.name)
                try:
                    subprocess.check_call("vboxmanage controlvm {} poweroff".format(vm.name).split(), \
                                   stdout=subprocess.PIPE)
                except subprocess.CalledProcessError:
                    print('VM shutdown failed!')
                    return {'rst': 'fail'}
                time.sleep(5)
                if vm.state != 1:
                    print('VM shutdown failed: %s' % vm.name)
                    return {'rst': 'fail'}
                else:
                    return {'rst': 'success'}
        return {'rst': 'fail'}

