// server.js
const express = require('express');
const cors = require('cors');
require('dotenv').config(); // load env variables
const authRoutes = require('./routes/authRoutes');

const app = express();

// If your frontend is on http://localhost:3000:
app.use(cors({
    origin: ['http://localhost:3000', 'http://localhost:3001'],
    credentials: true
}));

app.use(express.json());

// Our auth routes (login, register, protected route, etc.)
app.use('/auth', authRoutes);

// A default route
app.get('/', (req, res) => {
    res.send('Hello from the nJwt Auth Server!');
});

// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
