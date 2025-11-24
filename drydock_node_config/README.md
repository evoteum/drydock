# Ansible

> [!IMPORTANT]
> You probably don't need this.
>
> In normal operation, the lab uses zero Ansible.

We use Ansible only for the initial setup of the very first node in the cluster. After that, Tinkerbell steps in and
completely reprovisions that same inaugural node. Ansible is then not used until we rebuild the cluster.

Yes, you have understood correctly. We have no Ansible in day-to-day operation at all.
[Sorry Jeff](https://www.youtube.com/watch?v=kN0DxEj5WMI).

We also do not run Ansible directly, as it is run as part of the bootstrapper script. To rebuild the cluster, please see
main [README](../README.md).
