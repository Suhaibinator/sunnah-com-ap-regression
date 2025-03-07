Feature: API Connectivity Test

  Scenario: Test API1 connectivity
    Given url 'https://api.sunnah.com/v1/collections'
    And header X-API-Key = 'SiRM4QDDeO3f9bDqSO6tS3p9ey3CwpAb2JT9byxl'
    When method get
    Then status 200
    And print 'API1 response:', response

  Scenario: Test API2 connectivity
    Given url 'http://localhost:8084/v1/collections'
    And header X-API-Key = 'your-api-key-2'
    When method get
    Then status 200
    And print 'API2 response:', response
