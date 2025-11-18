import traceback


class OrchestrationError(Exception):
    pass


class OrchestrationResult:
    def __init__(
        self,
        success: bool,
        machine_ip: str = None,
        error_message: str = None,
        ip_prompted: bool = False,
    ):
        self.success = success
        self.machine_ip = machine_ip
        self.error_message = error_message
        self.ip_prompted = ip_prompted


def run_orchestration(
    machine_ip: str,
    tofu_init_func,
    tofu_apply_func,
    ansible_func,
):
    """
    * tofu init
    * tofu apply
    * ansible playbook
    """

    try:
        tofu_init_func()
    except Exception as exc:
        raise OrchestrationError(f"tofu init failed: {exc}") from exc

    try:
        tofu_apply_func()
    except Exception as exc:
        raise OrchestrationError(f"tofu apply failed: {exc}") from exc

    try:
        ansible_func(ip=machine_ip)
    except Exception as exc:
        tb = traceback.format_exc()
        raise OrchestrationError(f"Ansible execution failed: {exc}\n{tb}") from exc

    return OrchestrationResult(
        success=True,
        machine_ip=machine_ip,
        ip_prompted=True,
    )
