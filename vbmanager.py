import virtualbox as vb
import subprocess


services = {
    1: "CREATE_VM",
    2: "DELETE_VM"
}


class VBManager():
    def __init__(self, services):
        self.services = services
        self.vbox = vb.VirtualBox()

    def list_all(self):
        return self.services

    def create_config_VM(self):
        vms_name = [vm.name[len(vm.name)-1:] for vm in self.vbox.machines]
        isHotVM = False
        for vm in self.vbox.machines:
            if vm.state == 1 and vm.name != 'hostname':
                # start existed and power-offed VM.
                completedProcess = subprocess.run("vboxmanage startvm {} --type headless".format(vm.name).split(), \
                               stdout=subprocess.PIPE)
                completedProcess.check_returncode()
                isHotVM = True
                break
        if not isHotVM:
            # create a new VM by cloning.
            completedProcess = subprocess.run(
                "vboxmanage clonevm data1 --snapshot static-storm-cluster --name data{} --register"\
                    .format(str(self.vbox.machines.__len__())), \
                stdout=subprocess.PIPE)
            # config VM

            completedProcess.check_returncode()




