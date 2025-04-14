import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Container, Typography, Button, Box } from '@mui/material';

const NotFoundPage = () => {
    return (
        <Container maxWidth="sm" sx={{ textAlign: 'center', mt: 10 }}>
            <Typography variant="h2" gutterBottom>
                404
            </Typography>
            <Typography variant="h5" gutterBottom>
                Page Not Found
            </Typography>
            <Typography variant="body1" sx={{ mb: 4 }}>
                The page you're looking for doesn't exist or has been moved.
            </Typography>
            <Box>
                <Button
                    variant="contained"
                    color="primary"
                    component={RouterLink}
                    to="/"
                >
                    Go Home
                </Button>
            </Box>
        </Container>
    );
};

export default NotFoundPage;
