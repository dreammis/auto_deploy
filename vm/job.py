import yaml

from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.playbook.play import Play

from auto_deploy.settings import ansible_bin_path, role, ks_url, iso_url

loader = DataLoader()
play = Play()
options = type("Options", (), dict(
    connection="smart",
    module_path=[ansible_bin_path],
    forks=10,
    become=None,
    become_method=None,
    become_user=None,
    check=False,
    diff=False))()


class Job:
    def __init__(self):
        self._play = {"hosts": None, "gather_facts": "no", "tasks": ()}
        self.inventory = None
        self.variable_manager = None
        self.host = None

    def init_data(self, ip, password, user=None):
        self._play["hosts"] = ip
        self.inventory = InventoryManager(loader=loader)
        self.variable_manager = VariableManager(loader=loader, inventory=self.inventory)
        self.inventory.add_host(ip)
        self.host = self.inventory.get_host(ip)
        self.variable_manager.set_host_variable(self.host, "ansible_ssh_user", (user or "root"))
        self.variable_manager.set_host_variable(self.host, "ansible_ssh_pass", password)

    def run(self, callback=None):
        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=loader,
                options=options,
                passwords={},
                stdout_callback=callback,
            )
            tqm.run(play.load(self._play, variable_manager=self.variable_manager))
        finally:
            if tqm is not None:
                tqm.cleanup()

    def test_connection(self, ip, password):
        self.init_data(ip, password)

        self._play["tasks"] = [{"name": "test connection", "shell": "echo 'ok'", "register": "ok"}]

        self.run()

        var = self.variable_manager.get_vars()["hostvars"]
        unreachable = dict(list(var.items()))[ip]["ok"].get("unreachable")

        return [2, "connect failed"] if unreachable else [0, ""]

    def update_branches(self):
        self.init_data("localhost", "")

        with open(role / "var.yml", "r") as f:
            kv = yaml.load(f)
            self.variable_manager.set_host_variable(self.host, "git_user", kv["git_user"])
            self.variable_manager.set_host_variable(self.host, "git_password", kv["git_password"])

        with open(role / "tasks" / "0_upgrade_branch.yml", "r") as f:
            self._play["tasks"] = [*yaml.load(f)]

        self.run()

        var = self.variable_manager.get_vars()["hostvars"]
        branch = dict(list(var.items()))["localhost"]
        backend = branch.get("backend", {}).get("stdout_lines", ["dev3"])
        web_old = branch.get("web_old", {}).get("stdout_lines", ["dev"])
        web_new = branch.get("web_new", {}).get("stdout_lines", ["dev"])

        return [backend, web_old, web_new]

    def upgrade_app(self, vm_ip, vm_password, backend, web_old, web_new):
        self.init_data(vm_ip, vm_password)

        self.variable_manager.set_host_variable(self.host, "backend", backend)
        self.variable_manager.set_host_variable(self.host, "web_old", web_old)
        self.variable_manager.set_host_variable(self.host, "web_new", web_new)
        self.variable_manager.set_host_variable(self.host, "yjyx_templates_path", role / "templates")

        with open(role / "var.yml", "r") as f:
            for k, v in yaml.load(f).items():
                self.variable_manager.set_host_variable(self.host, k, v)

        with open(role / "tasks" / "5_upgrade.yml", "r") as f:
            self._play["tasks"] = [*yaml.load(f)]

        self.run()

        return ""

    def upgrade_paper(self):
        self.init_data("{{ip}}", "{{password}}", "{{user}}")

        with open(role / "var.yml", "r") as f:
            for k, v in yaml.load(f).items():
                self.variable_manager.set_host_variable(self.host, k, v)

        self.variable_manager.set_host_variable(self.host, "yjyx_templates_path", role / "templates")
        self.variable_manager.set_host_variable(self.host, "celery_broker_url", "{{amqp_url}}")
        self.variable_manager.set_host_variable(self.host, "mq_url", "118.178.129.156:15672")

        with open(role / "tasks" / "6_paper.yml", "r") as f:
            self._play["tasks"] = [*yaml.load(f)]

        self.run()

        return ""

    def create_vm_dir(self, store_path, vm_name, pm_ip, pm_password, cpu=2, mem=4, disk=50):
        self.init_data(pm_ip, pm_password)

        self.variable_manager.set_host_variable(self.host, "vm_name", vm_name)
        install_cmd = "virt-install --network bridge=br0 --name {0} --ram={1} --vcpus={2} --disk path={3}.img,size={4} --location={5} --extra-args='ks={6}' --graphics vnc"

        self._play["tasks"] = [
            {'name': 'sync pm dir', 'file': {'path': store_path, 'state': 'directory'}},
            {'name': 'virt-install', 'shell': install_cmd.format(vm_name, mem * 1024, cpu, (store_path + vm_name), disk, iso_url, ks_url)},
            {'name': 'sync vm mac', 'shell': """virsh domiflist {{ vm_name }} | awk '/:/ {print $5}'""", "register": "mac"},
            {'name': 'sync vm ip', 'shell': """arp -e | awk '$3=="{{ mac.stdout }}" {print$1}'""", "register": "ip"},
        ]

        self.run()

        var = self.variable_manager.get_vars()["hostvars"]
        resp = ["0.0.0.0", "", ""]
        var = dict(list(var.items()))[pm_ip]
        if var.get("mac"):
            resp[1] = var["mac"]["stdout"]
        else:
            resp[2] = "failed sync mac"
        if var.get("ip"):
            resp[0] = var["ip"]["stdout"]
        else:
            resp[2] = "failed sync ip"

        return resp

    def install_and_deploy(self, ip, password="1"):
        self.init_data(ip, password)

        with open(role / "var.yml", "r") as f:
            self.variable_manager.set_host_variable(self.host, "ansible_python_interpreter", "/usr/bin/python2")
            self.variable_manager.set_host_variable(self.host, "yjyx_templates_path", role / "templates")
            self.variable_manager.set_host_variable(self.host, "yjyx_files_path", role / "files")
            for k, v in yaml.load(f).items():
                self.variable_manager.set_host_variable(self.host, k, v)

        self._play["tasks"] = [
            *yaml.load(open(role / "tasks" / "1_base.yml", "r")),
            *yaml.load(open(role / "tasks" / "2_service.yml", "r")),
            *yaml.load(open(role / "tasks" / "3_opencv_ocr.yml", "r")),
            *yaml.load(open(role / "tasks" / "4_yjyx.yml", "r")),
        ]

        self.run()

        return ""

    def delete_vm_dir(self, ip, password, store_path, vm_name):
        self.init_data(ip, password)

        self._play["tasks"] = [
            {'shell': "virsh shutdown {}".format(vm_name), "ignore_errors": True},
            {'shell': "virsh undefine {}".format(vm_name), "ignore_errors": True},
            {'shell': "echo > /root/.ssh/known_hosts && /usr/bin/rm -rf {}{}".format(store_path, vm_name)},
        ]

        self.run()


job = Job()
