const http = require('http');

const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/chat') {
    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });
    req.on('end', () => {
      const message = JSON.parse(body).message;
      res.writeHead(200, {'Content-Type': 'text/plain'});
      res.end(`Message received: ${message}`);
    });
  } else {
    res.writeHead(404);
    res.end();
  }
});

server.listen(8081, () => {
  console.log('Server running on port 8081');
});