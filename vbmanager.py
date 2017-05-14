import virtualbox as vb
import time
import subprocess


services = {
    1: "CREATE_VM",
    2: "DELETE_VM",
    3: "MACHINES_STATS"
}
CLUSTER_MAX_SIZE = 7
CLUSTER_MIN_SIZE = 3


class VBManager:
    def __init__(self):
        self.services = services
        self.vbox = vb.VirtualBox()
        self.cold_vm_snapshot = 'supervisor'

    def machines_stats(self):
        num_running_machines = 0
        for vm in self.vbox.machines:
            if vm.state == 5:
                num_running_machines += 1
        return {'machinesTotal': len(self.vbox.machines),
                'machinesRunning': num_running_machines}

    def list_all(self):
        return {'rst': 'success', 'msg': self.services}

    def create_config_VM(self):
        isHotVM = False
        for vm in self.vbox.machines:
            if vm.state == 1 and vm.name != 'namenode':
                # start an existed and power-offed VM.
                isHotVM = True
                bootup_vm = vm.name
                break
        if not isHotVM:
            if self.vbox.machines.__len__() >= CLUSTER_MAX_SIZE:
                print('Cold VM creation failed: Beyond the cluster size limitation.')
                return {'rst': 'fail', 'msg': 'Cold VM creation failed: Beyond the cluster size limitation.'}
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
                return {'rst': 'fail', 'msg': 'Cold VM creation failed: Clone VM error.'}
            print('Starting a VM %s ...' % new_vm_name)
            try:
                subprocess.check_call("vboxmanage startvm {} --type headless".format(new_vm_name).split(), \
                                                  stdout=subprocess.PIPE)
            except subprocess.CalledProcessError:
                print('Cold VM creation failed: Start VM error.')
                return {'rst': 'fail', 'msg': 'Cold VM creation failed: Start VM error.'}
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
                    return {'rst': 'fail', 'msg': 'VM creation failed: Timeout.'}
            print('Configuring a VM %s ...' % new_vm_name)
            _, o, e = self.execute_cmd(vm, '/usr/bin/sudo', ['/home/storm/lab/config_VM.py', ('%s' % datanode_num)], 15)
            print('config output: ', o)
            print('config error: ', e)
            print('Saving state for VM %s ...' % new_vm_name)
            try:
                subprocess.check_call("vboxmanage controlvm {} savestate".format(new_vm_name).split(), \
                                      stdout=subprocess.PIPE)
            except subprocess.CalledProcessError:
                print('Cold VM creation failed: Savestate VM error.')
                return {'rst': 'fail', 'msg': 'Cold VM creation failed: Savestate VM error.'}
            time.sleep(10)
            bootup_vm = new_vm_name
        # start VM.
        print('Starting VM %s ...' % bootup_vm)
        try:
            subprocess.check_call("vboxmanage startvm {} --type headless".format(bootup_vm).split(), \
                                  stdout=subprocess.PIPE)
        except subprocess.CalledProcessError:
            print('Hot VM creation failed!')
            return {'rst': 'fail', 'msg': 'Hot VM creation failed!'}
        time.sleep(15)
        if not isHotVM:
            # restart to ensure the network configuration is OK.
            print('Restart VM %s to ensure the network configuration is OK ...' % bootup_vm)
            try:
                subprocess.check_call("vboxmanage controlvm {} reset".format(bootup_vm).split(), \
                                      stdout=subprocess.PIPE)
            except subprocess.CalledProcessError:
                print('Reset VM failed!')
                return {'rst': 'fail', 'msg': 'Reset VM failed!'}
            time.sleep(20)
        # check if VM is running.
        vm = self.vbox.find_machine(bootup_vm)
        timeout = 15
        while vm.state != 5:
            if timeout > 0:
                time.sleep(5)
                timeout -= 5
            else:
                print('VM creation failed: Timeout.')
                return {'rst': 'fail', 'msg': 'VM creation failed: Timeout.'}
        print('Starting datanode VM %s ...' % bootup_vm)
        # try:
        #     subprocess.check_call("vboxmanage guestcontrol {} run --exe /home/storm/lab/supervisor_up.py"
        #                           " --no-wait-stdout --no-wait-stderr --username storm --password 14641 ".format(bootup_vm).split(), \
        #                           stdout=subprocess.PIPE)
        # except subprocess.CalledProcessError:
        #     print('Starting datanode failed!')
        #     return {'rst': 'fail', 'msg': 'Starting datanode failed!'}
        # time.sleep(20)
        _, o, e = self.execute_cmd(vm=vm, cmd='/home/storm/lab/supervisor_up.py', params=[],
                                   waittime=20)
        print('Storm supervisor out: ', o)
        print('Storm supervisor err: ', e)
        return {'rst': 'success', 'msg': bootup_vm}

    def shrink_VM(self):
        num_running_vms = 0
        for vm in self.vbox.machines:
            if vm.state == 5:
                num_running_vms += 1
        if num_running_vms <= CLUSTER_MIN_SIZE:
            print('VM shinkage failed: Beyond the cluster size limitation.')
            return {'rst': 'fail', 'msg': 'VM shinkage failed: Beyond the cluster size limitation.'}
        for vm in self.vbox.machines:
            if vm.state == 5 and vm.name not in ['namenode', 'data1', 'data2']:
                # shutdown an existed and running VM.
                print('Shutdowning a VM %s ...' % vm.name)
                try:
                    subprocess.check_call("vboxmanage controlvm {} poweroff".format(vm.name).split(), \
                                   stdout=subprocess.PIPE)
                except subprocess.CalledProcessError:
                    print('VM shutdown failed!')
                    return {'rst': 'fail', 'msg': 'VM shutdown failed!'}
                time.sleep(10)
                if vm.state != 1:
                    print('VM shutdown failed: %s' % vm.name)
                    return {'rst': 'fail', 'msg': 'VM shutdown failed: %s' % vm.name}
                else:
                    return {'rst': 'success', 'msg': vm.name}
        return {'rst': 'fail'}

    def execute_cmd(self, vm, cmd, params, waittime):
        with vm.create_session() as session:
            time.sleep(15)
            with session.console.guest.create_session('storm', '14641') as gs:
                time.sleep(15)
                p, o, e = gs.execute(cmd, params, timeout_ms=waittime * 1000)
        return p, o, e

