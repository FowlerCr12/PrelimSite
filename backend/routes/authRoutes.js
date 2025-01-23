// routes/authRoutes.js
const express = require('express');
const { register, login, protect } = require('../controllers/authController');

const router = express.Router();

router.post('/register', register);
router.post('/login', login);

// Example protected route
router.get('/profile', protect, (req, res) => {
    // If we made it here, the token is valid
    res.status(200).json({
        message: 'Protected route data',
        user: req.user // includes your token claims (iss, sub, email, etc.)
    });
});

module.exports = router;
