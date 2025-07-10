const express = require('express');
const app = express();

app.get('/', (_, res) => res.send('Hello from Node.js Web Server!'));

app.listen(4000, () => {
  console.log('Web server running on http://localhost:4000');
});