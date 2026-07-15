import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';

/**
 * Application header with EHR branding.
 */
const Header = () => (
  <AppBar position="static" sx={{ backgroundColor: '#1a365d', boxShadow: '0 2px 8px rgba(0,0,0,0.15)' }}>
    <Toolbar>
      <LocalHospitalIcon sx={{ mr: 2, fontSize: 28 }} />
      <Typography variant="h6" component="div" sx={{ fontWeight: 700, letterSpacing: '0.02em' }}>
        CDS Hooks Sandbox
      </Typography>
    </Toolbar>
  </AppBar>
);

export default Header;
