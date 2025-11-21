Feature: Autodiscovery of inaugural bootstrap host
  As a user deploying a new metal Kubernetes cluster
  I want the bootstrapper to automatically detect the inaugural host
  So that I do not need to manually provide its IP address


  Background:
    Given the discovery subnet is "192.168.8.0/24"
    And the discovery retry interval is 2 seconds
    And the discovery total timeout is 10 seconds


  Scenario: Exactly one SSH host is discovered immediately
    Given the subnet contains a single SSH host at "192.168.8.12"
    When autodiscovery runs
    Then the result should be "192.168.8.12"


  Scenario: The SSH host appears after several retries
    Given the subnet initially has no SSH hosts
    And after 3 retries an SSH host appears at "192.168.8.12"
    When autodiscovery runs
    Then the result should be "192.168.8.12"
    And autodiscovery should have retried at least 3 times


  Scenario: No SSH hosts ever appear
    Given the subnet contains no SSH hosts
    When autodiscovery runs
    Then autodiscovery should fail with "No inaugural host found"


  Scenario: Multiple SSH hosts are detected
    Given the subnet contains a SSH host at "192.168.8.12"
    And the subnet also contains a SSH host at "192.168.8.34"
    When autodiscovery runs
    Then autodiscovery should fail with "Multiple SSH hosts detected"


  Scenario: A host responds to TCP but does not present an SSH banner
    Given the subnet contains a host at "192.168.8.20" with port 22 open
    And the host returns a non-SSH banner
    When autodiscovery runs
    Then autodiscovery should fail with "No inaugural host found"


  Scenario: Connection attempts time out
    Given all TCP connection attempts on port 22 time out
    When autodiscovery runs
    Then autodiscovery should fail with "No inaugural host found"


  Scenario: SSH banner is malformed but still contains 'ssh'
    Given the subnet contains a host at "192.168.8.12"
    And the SSH banner is "SSH-2.0-???SomethingWeird"
    When autodiscovery runs
    Then the result should be "192.168.8.12"


  Scenario: The SSH host appears briefly and vanishes before the next scan
    Given an SSH host appears only for one scan at "192.168.8.12"
    And it disappears on subsequent scans
    When autodiscovery runs
    Then the result should be "192.168.8.12"
    And autodiscovery should accept the first stable detection
