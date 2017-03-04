import virtualbox as vb
import subprocess
import time


services = {
    1: "CREATE_VM",
    2: "DELETE_VM"
}
CLUSTER_MAX_SIZE = 7


class VBManager:
    def __init__(self):
        self.services = services
        self.vbox = vb.VirtualBox()
        self.cold_vm_snapshot = 'scaling-in-vm-level'

    def list_all(self):
        return {'rst': 'success', 'data': self.services}

    def create_config_VM(self):
        isHotVM = False
        for vm in self.vbox.machines:
            if vm.state == 1 and vm.name != 'namenode':
                # start existed and power-offed VM.
                try:
                    subprocess.run("vboxmanage startvm {} --type headless".format(vm.name).split(), \
                                   stdout=subprocess.PIPE, check=True)
                except subprocess.CalledProcessError:
                    print('Hot VM creation failed!')
                    return {'rst': 'fail'}
                isHotVM = True
                break
        if not isHotVM:
            if self.vbox.machines.__len__() >= CLUSTER_MAX_SIZE:
                print('Cold VM creation failed: Beyond the cluster size limitation.')
                return {'rst': 'fail'}
            # create a new VM by cloning.
            try:
                new_vm_name = 'data' + str(self.vbox.machines.__len__())
                subprocess.run(
                    "vboxmanage clonevm data1 --snapshot {} --name {} --register"\
                        .format(self.cold_vm_snapshot, new_vm_name).split(), \
                    stdout=subprocess.PIPE, check=True)
            except subprocess.CalledProcessError:
                print('Cold VM creation failed: Clone VM error.')
                return {'rst': 'fail'}
            try:
                subprocess.run("vboxmanage startvm {} --type headless".format(new_vm_name).split(), \
                                                  stdout=subprocess.PIPE, check=True)
            except subprocess.CalledProcessError:
                print('Cold VM creation failed: Start VM error.')
                return {'rst': 'fail'}
            # config VM
            vm = self.vbox.find_machine(new_vm_name)
            while vm.state != 5:
                time.sleep(5)
            with vm.create_session() as session:
                with session.console.guest.create_session('storm', '14641') as gs:
                    process, stdout, stderr = gs.execute('sudo python3', ['/home/storm/lab/config_VM.py'])

        return {'rst': 'success'}


