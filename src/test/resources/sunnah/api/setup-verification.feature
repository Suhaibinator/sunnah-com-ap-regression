Feature: Setup Verification

  Scenario: Verify Karate setup
    * def greeting = 'Hello, World!'
    * match greeting == 'Hello, World!'
    * print 'Karate setup is working correctly!'
