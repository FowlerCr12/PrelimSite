// db/index.js
const mysql = require('mysql2/promise');
require('dotenv').config(); // Load .env if you are using environment variables

// Create the pool with your DB connection settings
const pool = mysql.createPool({
    host: process.env.DB_HOST,      // e.g. '34.44.xx.xx'
    user: process.env.DB_USER,      // e.g. 'root'
    password: process.env.DB_PASS,  // e.g. 'yourpassword'
    database: process.env.DB_NAME,  // e.g. 'document_manager'
    port: process.env.DB_PORT || 3306,
});

// Export the pool
module.exports = pool;
