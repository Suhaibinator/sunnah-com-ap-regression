Feature: Test Books Endpoints

  Background:
    * call read('common.feature')
    * def compareApi = call compareApiResponses
    * def logResults = call logComparisonResults

  Scenario Outline: Test GET /collections/{collectionName}/books/{bookNumber}/chapters endpoint
    * def result = compareApi('/collections/' + collectionName + '/books/' + bookNumber + '/chapters', null)
    * assert logResults(result)
    
    # Store chapters for further testing if available
    * eval if (result.response1.json.data && result.response1.json.data.length > 0) karate.write(result.response1.json.data, 'target/chapters_' + collectionName + '_' + bookNumber + '.json')

    Examples:
      * def collections = read('file:target/collections.json')
      * def examples = []
      * eval for (var i = 0; i < collections.length; i++) { var collectionName = collections[i].name; try { var books = read('file:target/books_' + collectionName + '.json'); for (var j = 0; j < books.length; j++) { examples.push({ collectionName: collectionName, bookNumber: books[j].bookNumber }); } } catch (e) { /* No books for this collection */ } }
      * table examples
        | collectionName | bookNumber |
        #(examples)

  Scenario Outline: Test GET /collections/{collectionName}/books/{bookNumber}/chapters/{chapterId} endpoint
    * def result = compareApi('/collections/' + collectionName + '/books/' + bookNumber + '/chapters/' + chapterId, null)
    * assert logResults(result)

    Examples:
      * def collections = read('file:target/collections.json')
      * def examples = []
      * eval for (var i = 0; i < collections.length; i++) { var collectionName = collections[i].name; try { var books = read('file:target/books_' + collectionName + '.json'); for (var j = 0; j < books.length; j++) { try { var chapters = read('file:target/chapters_' + collectionName + '_' + books[j].bookNumber + '.json'); for (var k = 0; k < chapters.length; k++) { examples.push({ collectionName: collectionName, bookNumber: books[j].bookNumber, chapterId: chapters[k].chapterId }); } } catch (e) { /* No chapters for this book */ } } } catch (e) { /* No books for this collection */ } }
      * table examples
        | collectionName | bookNumber | chapterId |
        #(examples)

  Scenario Outline: Test GET /collections/{collectionName}/books/{bookNumber}/hadiths endpoint
    * def result = compareApi('/collections/' + collectionName + '/books/' + bookNumber + '/hadiths', null)
    * assert logResults(result)
    
    # Store hadiths for further testing if available
    * eval if (result.response1.json.data && result.response1.json.data.length > 0) karate.write(result.response1.json.data, 'target/hadiths_' + collectionName + '_' + bookNumber + '.json')

    Examples:
      * def collections = read('file:target/collections.json')
      * def examples = []
      * eval for (var i = 0; i < collections.length; i++) { var collectionName = collections[i].name; try { var books = read('file:target/books_' + collectionName + '.json'); for (var j = 0; j < books.length; j++) { examples.push({ collectionName: collectionName, bookNumber: books[j].bookNumber }); } } catch (e) { /* No books for this collection */ } }
      * table examples
        | collectionName | bookNumber |
        #(examples)
