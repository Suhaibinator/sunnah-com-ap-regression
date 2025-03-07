Feature: Test Collections Endpoints

  Background:
    * call read('common.feature')
    * def compareApi = call compareApiResponses
    * def logResults = call logComparisonResults

  Scenario: Test GET /collections endpoint
    # Direct API calls to test connectivity
    * url apiImpl1.baseUrl + '/collections'
    * header X-API-Key = apiImpl1.apiKey
    * method get
    * def response1 = response
    * print 'API1 response status:', response.status
    
    * url apiImpl2.baseUrl + '/collections'
    * header X-API-Key = apiImpl2.apiKey
    * method get
    * def response2 = response
    * print 'API2 response status:', response.status
    
    # Compare responses
    * def comparison = compareResponses(response1, response2)
    * def result = { endpoint: '/collections', params: null, response1: response1, response2: response2, comparison: comparison }
    * assert logResults(result)
    
    # Store collections for further testing
    * def collections = response1.data
    * karate.write(collections, 'target/collections.json')

  Scenario Outline: Test GET /collections/{collectionName} endpoint
    * def result = compareApi('/collections/' + collectionName, null)
    * assert logResults(result)

    Examples:
      | collectionName |
      | bukhari        |
      | muslim         |

  Scenario Outline: Test GET /collections/{collectionName}/books endpoint
    * def result = compareApi('/collections/' + collectionName + '/books', null)
    * assert logResults(result)
    
    # Store books for further testing if the collection has books
    * eval if (result.response1.json.data && result.response1.json.data.length > 0) karate.write(result.response1.json.data, 'target/books_' + collectionName + '.json')

    Examples:
      | collectionName |
      | bukhari        |
      | muslim         |

  Scenario Outline: Test GET /collections/{collectionName}/books/{bookNumber} endpoint
    * def result = compareApi('/collections/' + collectionName + '/books/' + bookNumber, null)
    * assert logResults(result)

    Examples:
      | collectionName | bookNumber |
      | bukhari        | 1          |
      | muslim         | 1          |
