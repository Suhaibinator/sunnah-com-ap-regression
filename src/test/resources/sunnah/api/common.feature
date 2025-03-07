@ignore
Feature: Common reusable functions for API testing

  Background:
    * def sleep = function(millis){ java.lang.Thread.sleep(millis) }
    * def uuid = function(){ return java.util.UUID.randomUUID() + '' }
    * def getCurrentTimestamp = function(){ return java.lang.System.currentTimeMillis() }

  Scenario: Compare API responses
    * def compareApiResponses =
    """
    function(endpoint, params) {
      karate.log('compareApiResponses called with endpoint: ' + endpoint);
      
      try {
        // Make request to first API implementation
        var url1 = apiImpl1.baseUrl + endpoint;
        var headers1 = { 'X-API-Key': apiImpl1.apiKey };
        karate.log('API1 URL: ' + url1);
        
        // Make request to second API implementation
        var url2 = apiImpl2.baseUrl + endpoint;
        var headers2 = { 'X-API-Key': apiImpl2.apiKey };
        karate.log('API2 URL: ' + url2);
        
        // Make the requests
        karate.log('Making request to API1');
        var response1 = karate.call('classpath:sunnah/api/common.feature@makeRequest', { url: url1, headers: headers1, params: params }).result;
        
        karate.log('Making request to API2');
        var response2 = karate.call('classpath:sunnah/api/common.feature@makeRequest', { url: url2, headers: headers2, params: params }).result;
        
        // Compare responses
        karate.log('Comparing responses');
        var comparison = compareResponses(response1, response2);
        
        return {
          endpoint: endpoint,
          params: params,
          response1: response1,
          response2: response2,
          comparison: comparison
        };
      } catch (e) {
        karate.log('Error in compareApiResponses: ' + e);
        throw e;
      }
    }
    """
    
  @makeRequest
  Scenario: Make an API request
    * def printArg = function(arg) { karate.log('__arg: ' + JSON.stringify(arg)); return arg; }
    * def safeArg = printArg(__arg || { url: '', headers: {}, params: {} })
    Given url safeArg.url
    And headers safeArg.headers
    And params safeArg.params || {}
    When method get
    Then def result = response

  Scenario: Log comparison results
    * def logComparisonResults =
    """
    function(result) {
      karate.log('Testing endpoint: ' + result.endpoint);
      if (result.params) {
        karate.log('With params: ' + JSON.stringify(result.params));
      }
      
      if (result.comparison.equal) {
        karate.log('✅ Responses match');
      } else {
        karate.log('❌ Responses differ:');
        for (var i = 0; i < result.comparison.differences.length; i++) {
          karate.log('  - ' + result.comparison.differences[i]);
        }
      }
      
      return result.comparison.equal;
    }
    """
