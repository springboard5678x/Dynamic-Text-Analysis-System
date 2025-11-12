import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  useMediaQuery,
  useTheme,
  Box,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Analytics as AnalyticsIcon,
  History as HistoryIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import './Navigation.css';

const Navigation = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Text Analysis', icon: <AnalyticsIcon />, path: '/analysis' },
    { text: 'Analysis History', icon: <HistoryIcon />, path: '/history' },
  ];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNavigation = (path) => {
    navigate(path);
    setMobileOpen(false);
  };

  const drawer = (
    <Box sx={{ width: 250 }} role="presentation">
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" color="primary" fontWeight="bold">
          NarrativeNexus
        </Typography>
      </Box>
      <List>
        {menuItems.map((item) => (
          <ListItem
            key={item.text}
            button
            onClick={() => handleNavigation(item.path)}
            selected={location.pathname === item.path}
            sx={{
              borderRadius: 2,
              mx: 1,
              my: 0.5,
              '&.Mui-selected': {
                backgroundColor: 'primary.main',
                color: 'white',
                '& .MuiListItemIcon-root': {
                  color: 'white',
                },
              },
              '&.Mui-selected:hover': {
                backgroundColor: 'primary.dark',
              },
            }}
          >
            <ListItemIcon
              sx={{
                color: location.pathname === item.path ? 'white' : 'text.secondary',
                minWidth: 40,
              }}
            >
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <>
      <AppBar
        position="fixed"
        sx={{
          backgroundColor: 'white',
          color: 'text.primary',
          backdropFilter: 'blur(20px)',
        }}
      >
        <Toolbar>
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            <Typography
              variant="h6"
              component="div"
              sx={{
                fontWeight: 700,
                background: 'linear-gradient(135deg, #2E86AB 0%, #A23B72 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mr: 4,
              }}
            >
              NarrativeNexus
            </Typography>

            {!isMobile && (
              <Box sx={{ display: 'flex', gap: 1 }}>
                {menuItems.map((item) => (
                  <Button
                    key={item.text}
                    onClick={() => handleNavigation(item.path)}
                    startIcon={item.icon}
                    sx={{
                      color: location.pathname === item.path ? 'primary.main' : 'text.secondary',
                      fontWeight: location.pathname === item.path ? 600 : 400,
                      borderRadius: 3,
                      px: 3,
                      '&:hover': {
                        backgroundColor: 'primary.light',
                        color: 'white',
                      },
                    }}
                  >
                    {item.text}
                  </Button>
                ))}
              </Box>
            )}
          </Box>

          <Button
            variant="contained"
            onClick={() => handleNavigation('/analysis')}
            sx={{
              borderRadius: 3,
              px: 3,
              textTransform: 'none',
              fontWeight: 600,
            }}
          >
            Analyze Text
          </Button>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 250 },
        }}
      >
        {drawer}
      </Drawer>
    </>
  );
};

export default Navigation;