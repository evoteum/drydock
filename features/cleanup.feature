Feature: Cleanup

  Background:
    Given backend configuration is available

  Scenario: Cleanup runs after a failure
    Given a temporary working environment is created
    And an unexpected failure occurs during bootstrap
    When the bootstrap tool exits
    Then the temporary working environment is removed
    And any temporary cluster configuration is reverted