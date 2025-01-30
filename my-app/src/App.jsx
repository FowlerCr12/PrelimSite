// my-app/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import ForgotPassword from './pages/ForgotPassword';
import ProtectedRoute from './ProtectedRoute';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/forgot-password" element={<ForgotPassword />} />

                {/* Protect the /home route */}
                <Route
                    path="/home"
                    element={
                        <ProtectedRoute>
                            <HomePage />
                        </ProtectedRoute>
                    }
                />

                <Route path="*" element={<LoginPage />} />
            </Routes>
        </Router>
    );
}

export default App;
