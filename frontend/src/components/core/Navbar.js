// src/components/Navbar.jsx

import React, { useState } from 'react';
import {
    AppBar,
    Tabs,
    Tab,
    Toolbar,
    Typography,
    IconButton,
    Menu,
    MenuItem,
    Box
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import LogoutIcon from '@mui/icons-material/Logout';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme } from '@mui/material/styles';
import { useAuth } from '../../context/AuthContext';

function Navbar({ selectedTab, setSelectedTab, onLogout }) {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
    const [menuAnchor, setMenuAnchor] = useState(null);
    const { logout } = useAuth();

    

    const handleMenuOpen = (event) => {
        setMenuAnchor(event.currentTarget);
    };

    const handleMenuClose = () => {
        setMenuAnchor(null);
    };

    const handleLogoutClick = () => {
        logout();
    };

    return (
        <AppBar position="static" sx={{ backgroundColor: 'primary.main' }}>
            <Toolbar>
                <Typography
                    variant="h6"
                    onClick={() => setSelectedTab(0)}
                    sx={{
                        flexGrow: 1,
                        cursor: 'pointer',
                        color: 'white',
                    }}
                >
                    PopeBeats2Tube
                </Typography>

                {isMobile ? (
                    <>
                        <IconButton
                            color="inherit"
                            edge="end"
                            onClick={handleMenuOpen}
                        >
                            <MenuIcon />
                        </IconButton>
                        <Menu
                            anchorEl={menuAnchor}
                            open={Boolean(menuAnchor)}
                            onClose={handleMenuClose}
                        >
                            <MenuItem onClick={() => { setSelectedTab(0); handleMenuClose(); }}>
                                Instant Upload
                            </MenuItem>
                            <MenuItem onClick={() => { setSelectedTab(1); handleMenuClose(); }}>
                                Scheduled Upload
                            </MenuItem>
                            <MenuItem onClick={() => { setSelectedTab(2); handleMenuClose(); }}>
                                Upload Management
                            </MenuItem>
                            <MenuItem onClick={() => { handleLogoutClick(); handleMenuClose(); }}>
                                <LogoutIcon fontSize="small" sx={{ mr: 1 }} />
                                Logout
                            </MenuItem>
                        </Menu>
                    </>
                ) : (
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Tabs
                            value={selectedTab}
                            onChange={(e, newValue) => setSelectedTab(newValue)}
                            textColor="inherit"
                            indicatorColor="secondary"
                            sx={{
                                '& .MuiTabs-indicator': {
                                    backgroundColor: 'secondary.main',
                                },
                            }}
                        >
                            <Tab label="Instant Upload" />
                            <Tab label="Scheduled Upload" />
                            <Tab label="Upload Management" />
                        </Tabs>
                        <IconButton
                            color="inherit"
                            sx={{ ml: 2 }}
                            onClick={handleLogoutClick}
                            title="Logout"
                        >
                            <LogoutIcon />
                        </IconButton>
                    </Box>
                )}
            </Toolbar>
        </AppBar>
    );
}

export default Navbar;
