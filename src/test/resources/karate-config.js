function fn() {
  var env = karate.env;
  karate.log('karate.env =', env);
  if (!env) {
    env = 'dev';
  }
  
  var config = {
    env: env,
    apiImpl1: {
      baseUrl: 'https://api.sunnah.com/v1',
      apiKey: ''
    },
    apiImpl2: {
      baseUrl: 'http://localhost:8084/v1',
      apiKey: 'your-api-key-2'
    },
    compareResponses: function(response1, response2) {
      var result = {
        equal: true,
        differences: []
      };
      
      if (response1.status !== response2.status) {
        result.equal = false;
        result.differences.push('Status codes differ: ' + response1.status + ' vs ' + response2.status);
      }
      
      try {
        var body1 = response1.json;
        var body2 = response2.json;
        
        var diff = karate.match(body1, body2).error;
        if (diff) {
          result.equal = false;
          result.differences.push('Response bodies differ: ' + diff);
        }
      } catch (e) {
        result.equal = false;
        result.differences.push('Error comparing responses: ' + e);
      }
      
      return result;
    }
  };
  
  karate.configure('connectTimeout', 5000);
  karate.configure('readTimeout', 5000);
  
  return config;
}
