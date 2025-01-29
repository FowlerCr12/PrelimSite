// backend/controllers/authController.js
const bcrypt = require('bcrypt');
const nJwt = require('njwt');
const secureRandom = require('secure-random');
const pool = require('../db');
require('dotenv').config();

// 1) Parse the base64 key from .env back into a Buffer:
const base64Key = process.env.NJWT_SIGNING_KEY;
const signingKey = Buffer.from(base64Key, 'base64'); // This is your secret for nJwt

//--------------------------------------
// REGISTER
//--------------------------------------
exports.register = async (req, res) => {
    try {
        const { email, password } = req.body;
        if (!email || !password) {
            return res.status(400).json({ message: 'Email and password are required' });
        }

        // Check if user exists
        const [rows] = await pool.execute('SELECT id FROM users WHERE email = ?', [email]);
        if (rows.length > 0) {
            return res.status(400).json({ message: 'User already exists' });
        }

        // Hash password
        const saltRounds = 10;
        const passwordHash = await bcrypt.hash(password, saltRounds);

        // Insert user
        await pool.execute('INSERT INTO users (email, passwordHash) VALUES (?, ?)', [email, passwordHash]);

        return res.status(201).json({ message: 'User registered successfully' });
    } catch (error) {
        console.error('Register Error:', error);
        return res.status(500).json({ message: 'Internal server error' });
    }
};

//--------------------------------------
// LOGIN
//--------------------------------------
exports.login = async (req, res) => {
    try {
        const { email, password } = req.body;
        if (!email || !password) {
            return res.status(400).json({ message: 'Email and password are required' });
        }

        // Check if user exists
        const [rows] = await pool.execute(
            'SELECT id, passwordHash FROM users WHERE email = ?',
            [email]
        );
        if (rows.length === 0) {
            return res.status(400).json({ message: 'Invalid credentials' });
        }

        const user = rows[0];

        // Compare password
        const isMatch = await bcrypt.compare(password, user.passwordHash);
        if (!isMatch) {
            return res.status(400).json({ message: 'Invalid credentials' });
        }

        // Create nJwt token with claims
        const claims = {
            // Standard fields:
            iss: 'your-app-or-domain', // issuer
            sub: `user-${user.id}`,    // subject = user ID
            // Custom fields:
            email: email,
            // e.g. userId or roles
        };

        // Create the token
        let jwt = nJwt.create(claims, signingKey, 'HS256'); // default is HS256, but being explicit
        // Optionally set expiration:
        jwt.setExpiration(new Date().getTime() + 60 * 60 * 1000); // 1 hour from now

        // Compact it to a string to send to client
        const token = jwt.compact();

        // Return the token + user info if you like
        return res.status(200).json({
            message: 'Login successful',
            token,
            user: {
                id: user.id,
                email
            }
        });
    } catch (error) {
        console.error('Login Error:', error);
        return res.status(500).json({ message: 'Internal server error' });
    }
};

//--------------------------------------
// VERIFY TOKEN MIDDLEWARE
//--------------------------------------
exports.protect = (req, res, next) => {
    // Typically, the token is in the Authorization header as "Bearer <token>"
    const authHeader = req.headers.authorization;
    if (!authHeader) {
        return res.status(401).json({ message: 'No authorization header' });
    }

    const token = authHeader.split(' ')[1];
    if (!token) {
        return res.status(401).json({ message: 'Invalid token format' });
    }

    // Verify the token
    nJwt.verify(token, signingKey, 'HS256', (err, verifiedJwt) => {
        if (err) {
            console.error('Token verification error:', err);
            return res.status(401).json({ message: 'Token invalid or expired' });
        }

        // If successful, verifiedJwt.body holds the claims
        // e.g. verifiedJwt.body.sub, verifiedJwt.body.email, etc.
        req.user = verifiedJwt.body; // attach the claims to req.user
        next();
    });
};
