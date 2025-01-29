// src/components/LoginForm.jsx
import React, { useState } from 'react';
import { TextInput, PasswordInput, Button, Group, Text, Container, Title } from '@mantine/core';
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

            // For demonstration, we'll just alert success
            alert('Login successful!');
            // You might redirect the user to a dashboard, etc.
        } catch (err) {
            setError(err.response?.data?.message || 'An error occurred');
        }
    };

    return (
        <Container size="xs" padding="md">
            <Title order={2} align="center" mb="lg">Login</Title>
            <form onSubmit={handleSubmit}>
                {/* Email Field */}
                <TextInput
                    label="Email"
                    placeholder="user@example.com"
                    required
                    value={email}
                    onChange={(event) => setEmail(event.currentTarget.value)}
                    mb="md"
                    styles={{
                        input: {
                            border: '1px solid #ccc',
                            borderRadius: '8px',
                            '&:focus': {
                                borderColor: '#007bff',
                                boxShadow: '0 0 0 1px rgba(0, 123, 255, 0.5)',
                            },
                        },
                    }}
                />

                {/* Password Field */}
                <PasswordInput
                    label="Password"
                    placeholder="Your password"
                    required
                    mt="md"
                    value={password}
                    onChange={(event) => setPassword(event.currentTarget.value)}
                    mb="md"
                />

                {/* Error Message */}
                {error && (
                    <Alert variant="light" color="red" title="Could not sign in" icon={<IconAlertCircle size={16} />}>
                        {error}
                    </Alert>
                )}

                {/* Submit Button */}
                <Group position="right" mt="md">
                    <Button type="submit">Login</Button>
                </Group>
            </form>
        </Container>
    );
}

export default LoginForm;
