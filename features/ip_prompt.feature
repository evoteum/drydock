Feature: Operator input validation

  Scenario: Invalid IP address is rejected
    Given backend configuration is available
    When I enter an invalid IP address
    Then I am told that the address is invalid
    And I am prompted to try again

  Scenario: Valid IP address is accepted
    Given backend configuration is available
    When I enter a valid IP address
    Then the bootstrap continues