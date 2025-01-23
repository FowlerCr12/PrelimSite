// src/pages/HomePage.jsx
import React from 'react';

function HomePage() {
    return (
        <div style={{ width: '100%', height: '100vh', margin: 0, padding: 0 }}>
            <iframe
                title="Dash App"
                src="http://127.0.0.1:8050" // <-- URL of your Dash app
                style={{
                    width: '100%',
                    height: '100%',
                    border: 'none',
                }}
            />
        </div>
    );
}

export default HomePage;
