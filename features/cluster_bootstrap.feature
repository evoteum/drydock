Feature: Cluster bootstrap

  The operator can bootstrap a new cluster from scratch.

  Scenario: Successful bootstrap
    Given valid environment configuration
    And a new machine is available on the network
    When the operator runs the bootstrap tool
    Then the cluster is ready for GitOps takeover