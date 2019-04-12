from itertools import chain, groupby
from operator import itemgetter
from time import sleep

from django.db import models
from django.db.models import Q, F
from celery import shared_task

from vm.job import job
from vm.lock import lock


class BranchManager(models.Manager):
    def update_branch(self):
        self._update_branch.delay()

    def list_branches(self):
        branches = self.filter().values().order_by("project", "name")
        branches = groupby(branches, itemgetter("project"))
        new_branches = [[], [], []]
        for b in branches:
            new_branches[(b[0]-1)] = list(b[1])
        return new_branches

    @staticmethod
    @shared_task(ignore_result=True)
    def _update_branch():
        with lock("update_branch"):
            p1s, p2s, p3s = job.update_branches()

            branches = mm_Branch.all().values()
            for b in branches:
                if b["project"] == 1 and b["name"] in p1s:
                    p1s.remove(b["name"])
                elif b["project"] == 2 and b["name"] in p2s:
                    p2s.remove(b["name"])
                elif b["project"] == 3 and b["name"] in p3s:
                    p3s.remove(b["name"])

            p1s = (mm_Branch.model(project=1, name=name[:32]) for name in p1s)
            p2s = (mm_Branch.model(project=2, name=name[:32]) for name in p2s)
            p3s = (mm_Branch.model(project=3, name=name[:32]) for name in p3s)
            mm_Branch.bulk_create(chain(p1s, p2s, p3s))


class PmManager(models.Manager):
    def add_pm(self, ip, password=None):
        pm, status = self.get_or_create(
            ip=ip, defaults={"password": (password or "1")}
        )

        return pm, status

    def delete_pm(self, pm_id):
        count, _ = self.filter(id=pm_id, vm_num=0).delete()

        return count

    def modify_pm(self, pm_id, ip=None, password=None, vm_num=None):
        for_update = {}
        if ip is not None:
            for_update["ip"] = ip
        if password is not None:
            for_update["password"] = password
        if vm_num is not None:
            for_update["vm_num"] = vm_num
        if for_update:
            self.filter(id=pm_id).update(**for_update)

    def get_pm(self, pm_id):
        pm = self.filter(id=pm_id).values().last() or {}
        return pm

    def list_pms(self, last_id=0):
        q = Q() if last_id is 0 else Q(id__lt=last_id)
        pms = self.filter(q).order_by("-id").values("id", "ip")[:5]

        return pms

    @property
    def get_valid_one(self):
        pm = self.filter(vm_num__lt=3).order_by("id").first()

        return pm

    def operate_vm_num(self, pm_id, num):
        self.filter(id=pm_id).update(vm_num=F("vm_num") + num)


class VmManager(models.Manager):
    def add_vm(self, ip, vm_name, password, pm=None, backend=None, web_old=None, web_new=None):
        if ip:
            vm_name = ip.replace(".", "_")
        else:
            ip = "0.0.0.0"

        vm = self.filter(vm_name=vm_name).last()
        assert not vm, (1, "vm_name exists")

        defaults = {
            "vm_name": vm_name,
            "password": password,
        }
        if pm is not None:
            defaults["pm"] = pm
        if backend is not None:
            defaults["backend"] = backend
        if web_old is not None:
            defaults["web_old"] = web_old
        if web_new is not None:
            defaults["web_new"] = web_new

        vm, status = self.get_or_create(
            ip=ip,
            defaults=defaults
        )

        if status:
            if ip == "0.0.0.0":
                self.create_vm_ok.delay(vm.id, pm.store_path, vm_name, pm.ip, pm.password)
            else:
                self.add_vm_ok.delay(vm.id, ip, password)

        return vm, status

    @staticmethod
    @shared_task(ignore_result=True)
    def create_vm_ok(vm_id, store_path, vm_name, pm_ip, pm_password):
        ip, mac, content = job.create_vm_dir(store_path, vm_name, pm_ip, pm_password)
        if not content:
            for i in range(60):
                sleep(1)
                print(i)
            # content = job.install_and_deploy(ip)
        mm_Vm.modify_vm(vm_id, ip=ip, mac=mac, status=0, content=content, conn=0)

    @staticmethod
    @shared_task(ignore_result=True)
    def add_vm_ok(vm_id, ip, password):
        conn, content = job.test_connection(ip, password)
        mm_Vm.modify_vm(vm_id, conn=conn, content=content, status=0)

    def delete_vm(self, vm_id):
        vm = self.filter(id=vm_id).last()
        count = 0
        pm_id = 0
        if vm:
            pm = vm.pm
            count, _ = self.filter(id=vm_id).delete()

            if count and pm:
                pm_id = pm.id
                self.delete_vm_ok.delay(pm.ip, pm.password, pm.store_path, vm.vm_name)

        return count, pm_id

    @staticmethod
    @shared_task(ignore_result=True)
    def delete_vm_ok(pm_ip, pm_password, pm_store_path, vm_name):
        job.delete_vm_dir(pm_ip, pm_password, pm_store_path, vm_name)

    def modify_vm(self, vm_id, ip=None, mac=None, password=None,
                  pm=None, status=None, conn=None, content=None,
                  backend=None, web_old=None, web_new=None):
        for_update = {}
        if ip is not None:
            for_update["ip"] = ip
        if mac is not None:
            for_update["mac"] = mac
        if password is not None:
            for_update["password"] = password
            conn = 1
        if pm is not None:
            for_update["pm"] = pm
        if status is not None:
            for_update["status"] = status
        if conn is not None:
            for_update["conn"] = conn
        if content is not None:
            for_update["content"] = content
        if backend is not None:
            for_update["backend"] = backend
        if web_old is not None:
            for_update["web_old"] = web_old
        if web_new is not None:
            for_update["web_new"] = web_new
        if for_update:
            self.filter(id=vm_id).update(**for_update)

        if password:
            vm = self.filter(id=vm_id).last()
            if vm:
                self.add_vm_ok.delay(vm.id, vm.ip, password)

    def get_vm(self, vm_id):
        vm = self.filter(id=vm_id).annotate(
            vm_id=F("id"),
            backend_name=F("backend__name"),
            web_old_name=F("web_old__name"),
            web_new_name=F("web_new__name")
        ).values(
            "vm_name", "ip", "password", "status",
            "conn", "status", "content", "vm_id",
            "backend_name", "web_old_name", "web_new_name"
        ).last() or {}
        return vm

    def list_vms(self, last_id=0):
        q = Q() if last_id is 0 else Q(id__lt=last_id)
        vms = self.filter(q).order_by("-id").annotate(
            vm_id=F("id"),
            backend_name=F("backend__name"),
            web_old_name=F("web_old__name"),
            web_new_name=F("web_new__name")
        ).values(
            "vm_name", "ip", "password", "status",
            "conn", "status", "content", "vm_id",
            "backend_name", "web_old_name", "web_new_name"
        )[:5]

        return vms

    def upgrade(self, vm_id):
        vm = self.get_vm(vm_id)
        assert vm, (1, "vm not exists")
        assert (vm['status'] == 0 and vm['conn'] == 0), (1, "vm busy")

        assert (not self.filter(status=2).exists()), (1, "waiting for other vm upgrade finish")

        self._upgrade.delay(vm_id)

    @staticmethod
    @shared_task(ignore_result=True)
    def _upgrade(vm_id):
        mm_Vm.modify_vm(vm_id, status=2)
        vm = mm_Vm.filter(id=vm_id).values("ip", "password", "backend__name", "web_old__name", "web_new__name").last()
        if vm:
            backend = vm["backend__name"] or "dev3"
            web_old = vm["web_old__name"] or "dev"
            web_new = vm["web_new__name"] or "dev"
            content = job.upgrade_app(vm["ip"], vm["password"], backend, web_old, web_new)
            job.upgrade_paper()
            mm_Vm.modify_vm(vm_id, status=0, content=content)


class Branch(models.Model):
    name = models.CharField(max_length=32, default="dev")
    # 1 is backend, 2 is web old, 3 is web new
    project = models.PositiveSmallIntegerField(default=1)

    objects = BranchManager()


class Pm(models.Model):
    ip = models.CharField(max_length=39, default="0.0.0.0")
    password = models.CharField(max_length=32, default="1")
    store_path = models.CharField(max_length=32, default="/home/auto_deploy_dir/")
    vm_num = models.PositiveSmallIntegerField(default=0)

    objects = PmManager()


class Vm(models.Model):
    ip = models.CharField(max_length=39, default="0.0.0.0")
    mac = models.CharField(max_length=32, default="")
    password = models.CharField(max_length=32, default="1")
    vm_name = models.CharField(max_length=32, default="")
    pm = models.ForeignKey(Pm, models.DO_NOTHING, null=True, blank=True)

    # 0 is in use, 1 is install, 2 is upgrade
    status = models.PositiveSmallIntegerField(default=1)
    # 0 is check success, 1 is checking, 2 is check failed
    conn = models.PositiveSmallIntegerField(default=1)
    content = models.CharField(max_length=128, default="")

    backend = models.ForeignKey(Branch, models.DO_NOTHING, "backend", null=True, blank=True)
    web_old = models.ForeignKey(Branch, models.DO_NOTHING, "web_old", null=True, blank=True)
    web_new = models.ForeignKey(Branch, models.DO_NOTHING, "web_new", null=True, blank=True)

    objects = VmManager()


mm_Branch = Branch.objects
mm_Vm = Vm.objects
mm_Pm = Pm.objects
