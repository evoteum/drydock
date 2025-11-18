from bootstrap_runner.environment import validate_ip_address, InvalidIPAddressError


def prompt_for_ip(input_func=input, output_func=print):
    """
    Prompt the operator for an IP address until a valid one is entered.

    input_func and output_func are injectable to allow deterministic testing.
    """
    while True:
        output_func("Please enter the IP address of the new machine:")
        ip_input = input_func().strip()

        try:
            valid_ip = validate_ip_address(ip_input)
            return valid_ip
        except InvalidIPAddressError as exc:
            output_func(f"Invalid IP address: {exc}")
            output_func("Please try again.\n")
