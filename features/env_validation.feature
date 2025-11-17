Feature: Environment validation

  Scenario: Missing mandatory configuration
    Given required backend configuration is not available
    When I run the bootstrap tool
    Then I am informed that configuration is missing
    And the bootstrap process does not start