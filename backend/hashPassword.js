// hashPassword.js
const bcrypt = require('bcrypt');

async function hashPassword() {
    const plainPassword = 'password123';
    const hashed = await bcrypt.hash(plainPassword, 10);
    console.log('Bcrypt hash:', hashed);
}

hashPassword();
