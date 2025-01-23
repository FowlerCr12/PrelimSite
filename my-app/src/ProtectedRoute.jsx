// src/ProtectedRoute.jsx
import React from 'react';
import { Navigate } from 'react-router-dom';

function ProtectedRoute({ children }) {
    const token = localStorage.getItem('token');

    if (!token) {
        // If no token, redirect to /login
        return <Navigate to="/login" replace />;
    }

    // If token is present, render the child route
    return children;
}

export default ProtectedRoute;
