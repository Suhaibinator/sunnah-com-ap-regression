Feature: Test Hadiths Endpoints

  Background:
    * call read('common.feature')
    * def compareApi = call compareApiResponses
    * def logResults = call logComparisonResults

  Scenario Outline: Test GET /collections/{collectionName}/hadiths/{hadithNumber} endpoint
    * def result = compareApi('/collections/' + collectionName + '/hadiths/' + hadithNumber, null)
    * assert logResults(result)
    
    # Store URNs for further testing
    * eval if (result.response1.json && result.response1.json.hadith) { for (var i = 0; i < result.response1.json.hadith.length; i++) { if (result.response1.json.hadith[i].urn) { var urns = karate.jsonPath(karate.read('file:target/urns.json') || '[]', '$'); urns.push(result.response1.json.hadith[i].urn); karate.write(urns, 'target/urns.json'); } } }

    Examples:
      * def collections = read('file:target/collections.json')
      * def examples = []
      * eval for (var i = 0; i < collections.length; i++) { var collectionName = collections[i].name; try { var books = read('file:target/books_' + collectionName + '.json'); for (var j = 0; j < books.length; j++) { try { var hadiths = read('file:target/hadiths_' + collectionName + '_' + books[j].bookNumber + '.json'); for (var k = 0; k < Math.min(hadiths.length, 5); k++) { examples.push({ collectionName: collectionName, hadithNumber: hadiths[k].hadithNumber }); } } catch (e) { /* No hadiths for this book */ } } } catch (e) { /* No books for this collection */ } }
      * table examples
        | collectionName | hadithNumber |
        #(examples)

  Scenario Outline: Test GET /hadiths/{urn} endpoint
    * def result = compareApi('/hadiths/' + urn, null)
    * assert logResults(result)

    Examples:
      * def urns = karate.jsonPath(karate.read('file:target/urns.json') || '[]', '$')
      * def examples = []
      * eval for (var i = 0; i < Math.min(urns.length, 10); i++) { examples.push({ urn: urns[i] }); }
      * table examples
        | urn |
        #(examples)

  Scenario: Test GET /hadiths/random endpoint
    * def result = compareApi('/hadiths/random', null)
    * assert logResults(result)
