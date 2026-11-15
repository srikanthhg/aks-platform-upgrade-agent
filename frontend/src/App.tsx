import { AppBar, Avatar, Box, Button, Container, Toolbar, Typography } from '@mui/material';
import { AuthenticatedTemplate, UnauthenticatedTemplate, useMsal } from '@azure/msal-react';
import { BrowserRouter, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { Dashboard as DashboardIcon, Logout, Terminal } from '@mui/icons-material';
import Dashboard from './pages/Dashboard';
import Workflow from './pages/Workflow';

function Shell() {
  const { instance } = useMsal();
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <Box minHeight="100vh">
      <AppBar position="sticky" elevation={0} color="transparent" sx={{ borderBottom: 1, borderColor: 'divider', backdropFilter: 'blur(18px)' }}>
        <Toolbar sx={{ maxWidth: 1440, width: '100%', mx: 'auto', minHeight: 76 }}>
          <Avatar sx={{ bgcolor: 'primary.main', color: '#07111f', width: 40, height: 40, mr: 1.5, borderRadius: 2 }}>
            <Terminal />
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography fontWeight={800} letterSpacing={-0.4}>AKS Platform Agent</Typography>
            <Typography variant="caption" color="text.secondary">CLOUD OPERATIONS CENTER</Typography>
          </Box>
          <Button startIcon={<DashboardIcon />} color={location.pathname === '/' ? 'primary' : 'inherit'} onClick={() => navigate('/')}>Dashboard</Button>
          <Button startIcon={<Logout />} color="inherit" onClick={() => instance.logoutRedirect()} sx={{ ml: 1 }}>Sign out</Button>
        </Toolbar>
      </AppBar>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/workflows/:id" element={<Workflow />} />
      </Routes>
      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Typography variant="caption" color="text.disabled">AKS PLATFORM UPGRADE AGENT · SECURE OPERATIONS</Typography>
      </Container>
    </Box>
  );
}

export default function App() {
  const { instance } = useMsal();
  return (
    <BrowserRouter>
      <AuthenticatedTemplate><Shell /></AuthenticatedTemplate>
      <UnauthenticatedTemplate>
        <Box minHeight="100vh" display="grid" sx={{ placeItems: 'center', p: 3, background: 'radial-gradient(circle at 50% 15%, rgba(48,125,220,.2), transparent 38%)' }}>
          <Stack spacing={3} alignItems="center" textAlign="center" sx={{ maxWidth: 520 }}>
            <Avatar sx={{ width: 76, height: 76, bgcolor: 'primary.main', color: '#07111f', borderRadius: 3 }}><Terminal sx={{ fontSize: 40 }} /></Avatar>
            <Box>
              <Typography variant="h3" fontWeight={800} letterSpacing={-1.5}>AKS Platform Agent</Typography>
              <Typography color="text.secondary" sx={{ mt: 1 }}>Plan, validate and manage Kubernetes upgrades with a secure, guided workflow.</Typography>
            </Box>
            <Button size="large" variant="contained" onClick={() => instance.loginRedirect()} sx={{ px: 4 }}>Sign in with Microsoft Entra ID</Button>
            <Typography variant="caption" color="text.secondary">Authorized operators only · Microsoft Entra ID</Typography>
          </Stack>
        </Box>
      </UnauthenticatedTemplate>
    </BrowserRouter>
  );
}
