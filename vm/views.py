import ipaddress
import os

from django.http import HttpResponse, JsonResponse, QueryDict

from vm.models import mm_Branch, mm_Pm, mm_Vm


class Handler:
    def __init__(self):
        self.request = None
        self.response = None
        self.paras = None
        self.method = {
            "add_pm": self.handler_add_pm,
            "delete_pm": self.handler_delete_pm,
            "modify_pm": self.handler_modify_pm,
            "get_pm": self.handler_get_pm,
            "list_pms": self.handler_list_pms,

            "add_vm": self.handler_add_vm,
            "delete_vm": self.handler_delete_vm,
            "modify_vm": self.handler_modify_vm,
            "get_vm": self.handler_get_vm,
            "list_vms": self.handler_list_vms,

            "update_branch": self.handler_update_branch,
            "list_branches": self.handler_list_branches,
            "upgrade": self.handler_upgrade,
            "log": self.handler_log,
        }

    def handler_log(self):
        self.check()
        logs = os.popen("tail -n 50 /home/autodeploy/nohup.out | tac")

        raise Exception("<br/>".join(logs))

    def handler_add_pm(self):
        self.check(["ip"])
        ip = self.paras["ip"]

        try:
            version = ipaddress.ip_address(ip).version
        except ValueError:
            version = 0
        assert version is 4, (1, "invalid ipv4 address")

        password = self.paras.get("password")
        pm, status = mm_Pm.add_pm(ip, password)
        assert status, (1, "already exists")

    def handler_delete_pm(self):
        self.check(["pm_id"], ["pm_id"])
        pm_id = self.paras["pm_id"]
        count = mm_Pm.delete_pm(pm_id)
        assert count, (1, "delete failed")

    def handler_modify_pm(self):
        self.check(["pm_id"], ["pm_id"])
        pm_id = self.paras["pm_id"]
        password = self.paras.get("password")
        mm_Pm.modify_pm(pm_id, password=password)

    def handler_get_pm(self):
        self.check(["pm_id"], ["pm_id"])
        pm_id = self.paras["pm_id"]
        pm = mm_Pm.get_pm(pm_id)
        self.response["pm"] = pm

    def handler_list_pms(self):
        self.check_int(["last_id"])
        last_id = int(self.paras.get("last_id", 0))
        pms = mm_Pm.list_pms(last_id)
        self.response["pms"] = list(pms)

    def handler_add_vm(self):
        self.check_int(["backend_id", "web_old_id", "web_new_id"])
        ip = self.paras.get("ip", "")
        vm_name = self.paras.get("vm_name", "")
        password = self.paras.get("password", "1")

        pm = None
        try:
            version = ipaddress.ip_address(ip).version
        except ValueError:
            # assert False, (1, "need valid ip address")
            version = 0
        if version is not 4:
            ip = None
            password = "1"
            self.check_necessary(["vm_name"])
            pm = mm_Pm.get_valid_one
            assert pm is not None, (1, "lack pm resource")
        else:
            vm_name = ""

        backend_id = int(self.paras.get("backend_id", 0))
        web_old_id = int(self.paras.get("web_old_id", 0))
        web_new_id = int(self.paras.get("web_new_id", 0))
        ids = filter(bool, [backend_id, web_old_id, web_new_id])
        branches = mm_Branch.filter(id__in=ids)
        backend, web_old, web_new = None, None, None
        for branch in branches:
            if branch.project == 1:
                backend = branch
            elif branch.project == 2:
                web_old = branch
            elif branch.project == 3:
                web_new = branch

        vm, status = mm_Vm.add_vm(ip, vm_name, password, pm, backend, web_old, web_new)
        msg = "already exists" if vm.vm_name == vm_name else "waiting, pm was busy"
        assert status, (1, msg)

        if status and pm:
            mm_Pm.operate_vm_num(pm.id, 1)

    def handler_delete_vm(self):
        self.check(["vm_id"], ["vm_id"])
        vm_id = self.paras["vm_id"]
        count, pm_id = mm_Vm.delete_vm(vm_id)
        assert count, (1, "delete failed")

        if count:
            mm_Pm.operate_vm_num(pm_id, -1)

    def handler_modify_vm(self):
        self.check(["vm_id"], ["vm_id", "backend_id", "web_old_id", "web_new_id"])
        vm_id = self.paras["vm_id"]
        password = self.paras.get("password")

        if password:
            vm = mm_Vm.get_vm(vm_id)
            assert vm, (1, "vm not exists")
            assert (vm['status'] == 0 and vm['conn'] != 1), (1, "vm busy")

        backend_id = int(self.paras.get("backend_id", 0))
        web_old_id = int(self.paras.get("web_old_id", 0))
        web_new_id = int(self.paras.get("web_new_id", 0))
        ids = filter(bool, [backend_id, web_old_id, web_new_id])
        branches = mm_Branch.filter(id__in=ids)
        backend, web_old, web_new = None, None, None
        for branch in branches:
            if branch.project == 1:
                backend = branch
            elif branch.project == 2:
                web_old = branch
            elif branch.project == 3:
                web_new = branch

        mm_Vm.modify_vm(vm_id, password=password, backend=backend, web_old=web_old, web_new=web_new)

    def handler_get_vm(self):
        self.check(["vm_id"], ["vm_id"])
        vm_id = self.paras["vm_id"]
        vm = mm_Vm.get_vm(vm_id)
        if vm:
            vm["backend_name"] = vm["backend_name"] or "dev3"
            vm["web_old_name"] = vm["web_old_name"] or "dev"
            vm["web_new_name"] = vm["web_new_name"] or "dev"
        self.response["vm"] = vm

    def handler_list_vms(self):
        self.check_int(["last_id"])
        last_id = int(self.paras.get("last_id", 0))
        vms = mm_Vm.list_vms(last_id)
        for vm in vms:
            vm["backend_name"] = vm["backend_name"] or "dev3"
            vm["web_old_name"] = vm["web_old_name"] or "dev"
            vm["web_new_name"] = vm["web_new_name"] or "dev"
        self.response["vms"] = list(vms)

    def handler_update_branch(self):
        self.check()
        mm_Branch.update_branch()

    def handler_list_branches(self):
        self.check()
        branches = mm_Branch.list_branches()
        self.response["branches"] = branches

    def handler_upgrade(self):
        self.check(["vm_id"], ["vm_id"])
        vm_id = self.paras["vm_id"]
        mm_Vm.upgrade(vm_id)

    def dispatch(self, request):
        self.request = request
        self.response = {"status": 0, "message": ""}
        self.paras = {k: v for k, v in [*request.GET.items(),
                                        *(QueryDict(request.body).items()),
                                        *request.POST.items()]}

        action = self.paras.get("action")
        method = self.method.get(action)

        try:
            if hasattr(method, "__call__"):
                resp = method()
            else:
                resp = {"status": 1, "message": "error"}
        except AssertionError as e:
            resp = {"status": e.args[0][0], "message": e.args[0][1]}
        except Exception as e:
            return HttpResponse(e.args[0])

        return JsonResponse(resp or self.response)

    def check(self, necessary=(), int_=(), bool_=(), options=(None, ())):
        self.check_necessary(necessary)
        self.check_int(int_)
        self.check_bool(bool_)
        self.check_options(*options)

    def check_necessary(self, paras):
        msg = "lack parameter: {}"
        for para in paras:
            assert self.paras.get(para) is not None, (1, msg.format(para))

    def check_int(self, paras):
        msg = "parameter {}: must be positive integer"
        for para in paras:
            one = self.paras.get(para, "0")
            assert one.isdigit(), (1, msg.format(para))

    def check_bool(self, paras):
        msg = "parameter {}: choose in [0, 1]"
        for para in paras:
            one = self.paras.get(para, "0")
            assert one in ["0", "1"], (1, msg.format(para))

    def check_options(self, para, options):
        msg = "parameter {}: choose in {}"
        one = self.paras.get(para)
        if one is not None:
            assert one in map(str, options), (1, msg.format(para, list(options)))


handler = Handler()
