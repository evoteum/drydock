Feature: Network discovery

  Scenario: Network discovery fails gracefully
    Given backend configuration is available
    And the network cannot be scanned
    When I run the bootstrap tool
    Then I am warned about the scan failure
    And I am still able to provide a node IP address manually