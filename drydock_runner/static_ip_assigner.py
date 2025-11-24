import time
import paramiko


class StaticIPAssignmentError(Exception):
    pass


class StaticIPAssigner:
    def __init__(self, ssh_user, ssh_password=None, ssh_key_path=None, timeout=300):
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.ssh_key_path = ssh_key_path
        self.timeout = timeout

    def _connect(self, host):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            if self.ssh_key_path:
                key = paramiko.RSAKey.from_private_key_file(self.ssh_key_path)
                client.connect(
                    hostname=host,
                    username=self.ssh_user,
                    pkey=key,
                    timeout=10,
                )
            else:
                client.connect(
                    hostname=host,
                    username=self.ssh_user,
                    password=self.ssh_password,
                    timeout=10,
                )
        except Exception as exc:
            raise StaticIPAssignmentError(f"SSH connection to {host} failed: {exc}")

        return client

    def _wait_for_ssh(self, host, delay=5):
        deadline = time.time() + self.timeout

        while time.time() < deadline:
            try:
                client = self._connect(host)
                client.close()
                return True
            except StaticIPAssignmentError:
                time.sleep(delay)

        raise StaticIPAssignmentError(f"Host {host} did not become reachable on SSH.")

    @staticmethod
    def _generate_netplan_yaml(static_ip, gateway, nameservers, mask):
        return f"""\
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: no
      addresses: [{static_ip}/{mask}]
      gateway4: {gateway}
      nameservers:
        addresses: [{", ".join(nameservers)}]
"""

    def assign(
        self,
        dhcp_ip,
        static_ip,
        gateway,
        nameservers=None,
        hostname=None,
        mask=24,
    ):
        if nameservers is None:
            nameservers = ["1.1.1.1", "8.8.8.8"]

        client = self._connect(dhcp_ip)

        if hostname:
            _, stdout, _ = client.exec_command("hostname")
            remote_hostname = stdout.read().decode().strip()

            if remote_hostname != hostname:
                client.close()
                raise StaticIPAssignmentError(
                    f"Refusing to configure host '{remote_hostname}'. "
                    f"Expected '{hostname}'."
                )

        if hostname:
            _, stdout, _ = client.exec_command(
                f"sudo hostnamectl set-hostname {hostname}"
            )
            stdout.channel.recv_exit_status()

            hosts_fix = f"127.0.1.1 {hostname}\n"
            cmd = f"echo '{hosts_fix}' | sudo tee -a /etc/hosts"
            client.exec_command(cmd)

        netplan_yaml = self._generate_netplan_yaml(
            static_ip=static_ip,
            gateway=gateway,
            nameservers=nameservers,
            mask=mask,
        )

        sftp = client.open_sftp()
        remote_path = "/etc/netplan/99-static.yaml"

        with sftp.open(remote_path, "w") as f:
            f.write(netplan_yaml)

        sftp.close()

        _, stdout, _ = client.exec_command("sudo netplan apply || sudo reboot")
        stdout.channel.recv_exit_status()

        client.close()
        self._wait_for_ssh(static_ip)

        return True
