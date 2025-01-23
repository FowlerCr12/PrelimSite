// generateKey.js
const secureRandom = require('secure-random');
const fs = require('fs');

const signingKeyBuffer = secureRandom(256, { type: 'Buffer' });
// Convert to base64 so we can store it in a file or .env
const base64SigningKey = signingKeyBuffer.toString('base64');

fs.writeFileSync('signingKey.txt', base64SigningKey);
console.log('Generated Key (base64) saved to signingKey.txt:', base64SigningKey);
