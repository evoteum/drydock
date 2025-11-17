#!/usr/bin/env python3

import sys
import tempfile

from dotenv import load_dotenv


from python.clean import run_cleanup, CleanupError
from python.cluster_build import run_bootstrap
from python.environment import EnvironmentValidationError
from python.orchestration import OrchestrationError


def main():
    """
    Entry point for the Kubernetes lab bootstrap tool.

    Responsibilities:
      1. Create a temporary working directory.
      2. Validate environment configuration and operator input.
      3. Execute discovery, tofu stages and Ansible provisioning.
      4. Report success or failure clearly.
      5. Perform cleanup unconditionally.
    """
    load_dotenv()
    tmp_dir = tempfile.mkdtemp(prefix="k8s-lab-bootstrap-")
    print(f"[INFO] Working directory created at: {tmp_dir}")
    print("[INFO] Starting cluster bootstrap process...")

    try:
        result = run_bootstrap(tmp_dir=tmp_dir)

        if result.discovery_warning:
            print("[WARN] Network discovery did not succeed. Manual IP entry was required.")

        if result.success:
            print("[SUCCESS] Cluster bootstrapped successfully.")
            if result.machine_ip:
                print(f"[INFO] Node IP address: {result.machine_ip}")
            return 0

        print("[ERROR] Cluster bootstrap failed.")
        if result.error_message:
            print("        " + str(result.error_message))
        return 1

    except EnvironmentValidationError as exc:
        print("[ERROR] Environment configuration is invalid:")
        print("        " + str(exc))
        return 2

    except OrchestrationError as exc:
        print("[ERROR] Orchestration error:")
        print("        " + str(exc))
        return 3

    finally:
        try:
            run_cleanup(tmp_dir)
            print("[INFO] Temporary directory cleaned.")
        except CleanupError as exc:
            print("[ERROR] Cleanup failed:")
            print("        " + str(exc))


if __name__ == "__main__":
    sys.exit(main())