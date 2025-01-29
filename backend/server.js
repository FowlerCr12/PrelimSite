// backend/server.js
require('dotenv').config(); // Load environment variables from .env
const express = require('express');
const cors = require('cors');
const authRoutes = require('./routes/authRoutes'); // or wherever your routes are

const app = express();

// Change origins to your Droplet's IP if you want to allow requests from it or from anywhere else
app.use(cors({
    origin: [
        'http://159.223.146.87' // your droplet IP (or other domains if needed)
    ],
    credentials: true,
}));

app.use(express.json());

// Example auth routes
app.use('/auth', authRoutes);

// Default route
app.get('/', (req, res) => {
    res.send('Hello from the nJwt Auth Server!');
});

// Start the server on port 5000, bound to localhost (127.0.0.1)
const PORT = process.env.PORT || 5000;
app.listen(PORT, '127.0.0.1', () => {
    console.log(`Server running on http://127.0.0.1:${PORT}`);
});
