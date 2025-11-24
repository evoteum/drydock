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


def run_orchestration(node_ip_address: str, ansible_func):
    try:
        ansible_func(node_ip_address)
    except Exception as exc:
        tb = traceback.format_exc()
        return OrchestrationResult(
            success=False,
            machine_ip=node_ip_address,
            error_message=f"Ansible execution failed: {exc}\n{tb}",
        )

    return OrchestrationResult(
        success=True,
        machine_ip=node_ip_address,
        ip_prompted=True,
    )
