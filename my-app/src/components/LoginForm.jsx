// src/components/LoginForm.jsx
import React, { useState } from 'react';
import { TextInput, PasswordInput, Button, Group, Text } from '@mantine/core';
import axios from 'axios';

function LoginForm() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        try {
            // Make sure this matches your backend login endpoint
            const response = await axios.post('http://localhost:5000/auth/login', {
                email,
                password,
            });

            // On success, store the token (e.g., localStorage or other method)
            localStorage.setItem('token', response.data.token);

            // For demonstration, we’ll just alert success
            alert('Login successful!');
            // You might redirect the user to a dashboard, etc.
        } catch (err) {
            setError(err.response?.data?.message || 'An error occurred');
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            {/* Email Field */}
            <TextInput
                label="Email"
                placeholder="name@example.com"
                required
                value={email}
                onChange={(event) => setEmail(event.currentTarget.value)}
            />

            {/* Password Field */}
            <PasswordInput
                label="Password"
                placeholder="Your password"
                required
                mt="md"
                value={password}
                onChange={(event) => setPassword(event.currentTarget.value)}
            />

            {/* Error Message */}
            {error && (
                <Text color="red" size="sm" mt="sm">
                    {error}
                </Text>
            )}

            {/* Submit Button */}
            <Group position="right" mt="md">
                <Button type="submit">Login</Button>
            </Group>
        </form>
    );
}

export default LoginForm;
