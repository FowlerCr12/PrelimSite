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
import { useEffect } from 'react';
// 1) Mantine styling
const useStyles = createStyles((theme) => ({
    wrapper: {
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#F5F5F5',
        maxHeight: '150vh',
    },
    formContainer: {
        maxWidth: 420,
        width: '100%',
        padding: theme.spacing.xl * 2,
        margin: 'auto',
        boxShadow: theme.shadows.md,
        backgroundColor: '',
        borderRadius: theme.radius.md,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        border: '2px solid #40739C',
        borderRadius: '20px',
        height: '400px',
        maxHeight: '500px',
    },
    button: {
        backgroundColor: 'white',
        borderRadius: '20px',
        height: '45px',
        width: '250px',
        marginBottom: '10px',
        fontSize: '16px',
        transition: 'all 0.2s ease',
        '&:hover': {
            backgroundColor: '#9ABBD6 !important',
        }
    },
    input: {
        border: '2px solid #7D7382',
        borderRadius: '20px',
        height: '45px',
        marginTop: '10px',
        width: '250px',
        marginBottom: '10px',
        fontSize: '16px',
        transition: 'all 0.2s ease',
        paddingLeft: '5px',
        '&:focus': {
            borderColor: '#40739C',
            boxShadow: '0 0 0 1px #40739C',
        },
        '&:hover': {
            borderColor: '#40739C',
            boxShadow: '0 0 0 1px #40739C',
        },
        '&::placeholder': {
            padding: '5px',
        }
    },
    label: {
        fontSize: '20px',
        marginTop: '10px',
    },
}));

function ForgotPassword() {
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
            const response = await axios.post('http://159.223.146.87/auth/login', {
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
                <Title order={2} align="center" mb="s">
                    Enter email to reset password.
                </Title>

                {/* Mantine Form */}
                <form onSubmit={form.onSubmit(handleSubmit)}>
                    <TextInput
                        label="Email"
                        placeholder="user@example.com"
                        required
                        mb="md"
                        {...form.getInputProps('email')}
                        classNames={{
                            input: classes.input,
                            label: classes.label,
                        }}
                    />

                    {/* If there's an error, show it */}
                    {errorMessage && (
                        <Text color="red" size="sm" mt="sm">
                            {errorMessage}
                        </Text>
                    )}

                    <Group position="center" mt="xl">
                        <Button
                            fullWidth
                            type="submit"
                            leftIcon={<IconLogin size={18} />}
                            classNames={{
                                root: classes.button,
                            }}
                        >
                            Submit
                        </Button>
                    </Group>
                </form>
            </Paper>
        </Box>
    );
}

export default ForgotPassword;