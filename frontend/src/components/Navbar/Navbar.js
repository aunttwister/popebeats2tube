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
    Box,
    Divider
} from '@mui/material';

import LogoutIcon from '@mui/icons-material/Logout';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import SettingsIcon from '@mui/icons-material/Settings';
import SubscriptionsIcon from '@mui/icons-material/Subscriptions';
import MenuIcon from '@mui/icons-material/Menu';

import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme } from '@mui/material/styles';
import { useAuth } from '../../context/AuthContext';

import './Navbar.css';
import { getUserEmail } from '../../utils/tokenManager';

function Navbar({ selectedTab, setSelectedTab }) {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
    const [navMenuAnchor, setNavMenuAnchor] = useState(null);
    const [userMenuAnchor, setUserMenuAnchor] = useState(null);
    const { logout } = useAuth();

    const userEmail = getUserEmail() || 'User';

    const handleNavMenuOpen = (e) => setNavMenuAnchor(e.currentTarget);
    const handleUserMenuOpen = (e) => setUserMenuAnchor(e.currentTarget);

    const handleMenuClose = () => {
        setNavMenuAnchor(null);
        setUserMenuAnchor(null);
    };

    const handleLogoutClick = () => {
        logout();
        handleMenuClose();
    };

    return (
        <AppBar position="static" className="navbar-appbar">
            <Toolbar className="navbar-toolbar">
                <Typography
                    variant="h6"
                    onClick={() => setSelectedTab(0)}
                    className="navbar-title"
                >
                    PopeBeats2Tube
                </Typography>

                {isMobile ? (
                    <>
                        <IconButton
                            color="inherit"
                            onClick={handleNavMenuOpen}
                        >
                            <MenuIcon />
                        </IconButton>
                        <Menu
                            anchorEl={navMenuAnchor}
                            open={Boolean(navMenuAnchor)}
                            onClose={handleMenuClose}
                        >
                            <MenuItem onClick={() => { setSelectedTab(0); handleMenuClose(); }}>Instant Upload</MenuItem>
                            <MenuItem onClick={() => { setSelectedTab(1); handleMenuClose(); }}>Scheduled Upload</MenuItem>
                            <MenuItem onClick={() => { setSelectedTab(2); handleMenuClose(); }}>Upload Management</MenuItem>
                            <Divider />
                            <MenuItem disabled className="navbar-user-greeting">Hello, {userEmail}</MenuItem>
                            <MenuItem disabled>
                                <SettingsIcon fontSize="small" className="navbar-icon" />
                                Upload Settings
                            </MenuItem>
                            <MenuItem disabled>
                                <SubscriptionsIcon fontSize="small" className="navbar-icon" />
                                Subscription
                            </MenuItem>
                            <MenuItem onClick={handleLogoutClick}>
                                <LogoutIcon fontSize="small" className="navbar-icon" />
                                Logout
                            </MenuItem>
                        </Menu>
                    </>
                ) : (
                    <Box className="navbar-tabs-container">
                        <Tabs
                            value={selectedTab}
                            onChange={(e, newValue) => setSelectedTab(newValue)}
                            textColor="inherit"
                            indicatorColor="secondary"
                            className="navbar-tabs"
                        >
                            <Tab label="Instant Upload" />
                            <Tab label="Scheduled Upload" />
                            <Tab label="Upload Management" />
                        </Tabs>

                        <Box className="navbar-divider" />

                        <IconButton
                            color="inherit"
                            onClick={handleUserMenuOpen}
                            title="User Menu"
                        >
                            <AccountCircleIcon />
                        </IconButton>
                        <Menu
                            anchorEl={userMenuAnchor}
                            open={Boolean(userMenuAnchor)}
                            onClose={handleMenuClose}
                        >
                            <MenuItem className="navbar-user-greeting">Hello, {userEmail}</MenuItem>
                            <MenuItem disabled>
                                <SettingsIcon fontSize="small" className="navbar-icon" />
                                Upload Settings
                            </MenuItem>
                            <MenuItem disabled>
                                <SubscriptionsIcon fontSize="small" className="navbar-icon" />
                                Subscription
                            </MenuItem>
                            <MenuItem onClick={handleLogoutClick}>
                                <LogoutIcon fontSize="small" className="navbar-icon" />
                                Logout
                            </MenuItem>
                        </Menu>
                    </Box>
                )}
            </Toolbar>
        </AppBar>
    );
}

export default Navbar;
