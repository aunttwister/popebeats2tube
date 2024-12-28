import React, { useState } from 'react';
import { AppBar, Tabs, Tab, Toolbar, Typography, IconButton, Menu, MenuItem } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme } from '@mui/material/styles';

function Navbar({ selectedTab, setSelectedTab }) {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm')); // Check if screen size is small
    const [menuAnchor, setMenuAnchor] = useState(null);

    const handleMenuOpen = (event) => {
        setMenuAnchor(event.currentTarget);
    };

    const handleMenuClose = () => {
        setMenuAnchor(null);
    };

    return (
        <AppBar position="static" sx={{ backgroundColor: 'primary.main' }}>
            <Toolbar>
                <Typography
                    variant="h6"
                    onClick={() => setSelectedTab(0)} // Resets the tab to 0
                    sx={{
                        flexGrow: 1,
                        cursor: 'pointer',
                        color: 'white', // Ensures the text is white
                    }}
                >
                    PopeBeats2Tube
                </Typography>
                {isMobile ? (
                    // Mobile view: Show hamburger menu
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
                        </Menu>
                    </>
                ) : (
                    // Desktop view: Show tabs
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
                )}
            </Toolbar>
        </AppBar>
    );
}

export default Navbar;
