import React, { useState } from 'react';
import {
    TextInput,
    PasswordInput,
    Button,
    Paper,
    Title,
    Text,
    Group,
    Box,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { IconLogin } from '@tabler/icons-react';
import { createStyles } from '@mantine/styles';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

// 1) Mantine styling
const useStyles = createStyles((theme) => ({
    wrapper: {
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: `linear-gradient(45deg, ${theme.colors.blue[6]}, ${theme.colors.cyan[3]})`,
    },
    formContainer: {
        maxWidth: 420,
        width: '100%',
        padding: theme.spacing.xl,
        boxShadow: theme.shadows.md,
    },
}));

function LoginPage() {
    const { classes } = useStyles();
    const navigate = useNavigate();

    // 2) Track error messages
    const [errorMessage, setErrorMessage] = useState('');

    // 3) Mantine form setup
    const form = useForm({
        initialValues: {
            email: '',
            password: '',
        },
        validate: {
            email: (value) => (/^\S+@\S+\.\S+$/.test(value) ? null : 'Invalid email'),
            password: (value) => (value.length < 6 ? 'Password must have at least 6 characters' : null),
        },
    });

    // 4) Actual submit handler
    const handleSubmit = async (values) => {
        setErrorMessage(''); // clear previous errors
        try {
            // Make an axios request to your backend
            const response = await axios.post('http://localhost:5000/auth/login', {
                email: values.email,
                password: values.password,
            });

            // If successful, the server typically returns a token and user data
            console.log('Login Response:', response.data);

            // Example: store token in localStorage
            localStorage.setItem('token', response.data.token);

            // Redirect to /home or whatever route you desire
            navigate('/home');
        } catch (error) {
            console.error('Login Error:', error);
            // Show an error message if credentials are invalid or request fails
            setErrorMessage(error.response?.data?.message || 'Login failed');
        }
    };

    return (
        <Box className={classes.wrapper}>
            <Paper radius="md" withBorder className={classes.formContainer}>
                <Title order={2} align="center" mb="xl">
                    Welcome Back
                </Title>

                {/* Mantine Form */}
                <form onSubmit={form.onSubmit(handleSubmit)}>
                    <TextInput
                        label="Email"
                        placeholder="user@example.com"
                        required
                        {...form.getInputProps('email')}
                    />

                    <PasswordInput
                        label="Password"
                        placeholder="Your password"
                        required
                        mt="md"
                        {...form.getInputProps('password')}
                    />

                    {/* If there's an error, show it */}
                    {errorMessage && (
                        <Text color="red" size="sm" mt="sm">
                            {errorMessage}
                        </Text>
                    )}

                    <Group position="apart" mt="md">
                        <Text color="dimmed" size="sm">
                            Forgot password?
                        </Text>
                    </Group>

                    <Button
                        fullWidth
                        mt="xl"
                        type="submit"
                        leftIcon={<IconLogin size={18} />}
                    >
                        Sign in
                    </Button>
                </form>
            </Paper>
        </Box>
    );
}

export default LoginPage;