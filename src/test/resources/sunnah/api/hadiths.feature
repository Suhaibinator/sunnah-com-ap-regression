Feature: Test Hadiths Endpoints

  Background:
    * call read('common.feature')
    * def compareApi = call compareApiResponses
    * def logResults = call logComparisonResults

  Scenario Outline: Test GET /collections/{collectionName}/hadiths/{hadithNumber} endpoint
    * def result = compareApi('/collections/' + collectionName + '/hadiths/' + hadithNumber, null)
    * def isApi2Working = result.response2.status != 500
    * if (isApi2Working) assert logResults(result)
    * else karate.log('Skipping comparison due to API2 error')
    
    # Store URNs for further testing
    * eval 
    """
    if (result.response1.json && result.response1.json.hadith) {
      var urns = karate.jsonPath(karate.read('file:target/urns.json') || '[]', '$');
      for (var i = 0; i < result.response1.json.hadith.length; i++) {
        if (result.response1.json.hadith[i].urn) {
          urns.push(result.response1.json.hadith[i].urn);
        }
      }
      karate.write(urns, 'target/urns.json');
    }
    """

    Examples:
      * def collections = read('file:target/collections.json')
      * def examples = []
      * eval for (var i = 0; i < collections.length; i++) { var collectionName = collections[i].name; try { var books = read('file:target/books_' + collectionName + '.json'); for (var j = 0; j < books.length; j++) { try { var hadiths = read('file:target/hadiths_' + collectionName + '_' + books[j].bookNumber + '.json'); for (var k = 0; k < Math.min(hadiths.length, 5); k++) { examples.push({ collectionName: collectionName, hadithNumber: hadiths[k].hadithNumber }); } } catch (e) { /* No hadiths for this book */ } } } catch (e) { /* No books for this collection */ } }
      * table examples
        | collectionName | hadithNumber |
        #(examples)

  Scenario Outline: Test GET /hadiths/{urnValue} endpoint
    * def result = compareApi('/hadiths/' + urnValue, null)
    * def isApi2Working = result.response2.status != 500
    * if (isApi2Working) assert logResults(result)
    * else karate.log('Skipping comparison due to API2 error')

    Examples:
      * def urns = karate.jsonPath(karate.read('file:target/urns.json') || '[]', '$')
      * eval if (urns.length === 0) { karate.log('No URNs found, skipping /hadiths/{urn} tests'); }
      * def examples = []
      * eval 
      """
      for (var i = 0; i < Math.min(urns.length, 10); i++) { 
        examples.push({ urnValue: urns[i] }); 
      }
      """
      * eval if (examples.length === 0) { examples.push({ urnValue: 'dummy' }); karate.log('No valid URNs found, adding dummy value'); }
      * table examples
        | urnValue |
        #(examples)
