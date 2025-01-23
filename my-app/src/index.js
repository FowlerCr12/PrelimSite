import React from 'react';
import ReactDOM from 'react-dom/client';
import { MantineProvider } from '@mantine/core';
import App from './App';

const rootEl = document.getElementById('root');
const root = ReactDOM.createRoot(rootEl);

root.render(
    <MantineProvider withGlobalStyles withNormalizeCSS>
        <App />
    </MantineProvider>
);
