import React from 'react';
import { AppBar, Tabs, Tab, Toolbar, Typography } from '@mui/material';

function Navbar({ selectedTab, setSelectedTab }) {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          PopeBeats2Tube
        </Typography>
        <Tabs
          value={selectedTab}
          onChange={(e, newValue) => setSelectedTab(newValue)}
          textColor="inherit"
          indicatorColor="secondary"
        >
          <Tab label="Instant Upload" />
          <Tab label="Scheduled Upload" />
          <Tab label="Upload Management" />
        </Tabs>
      </Toolbar>
    </AppBar>
  );
}

export default Navbar;
