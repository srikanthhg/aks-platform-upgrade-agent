import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#66b3ff', light: '#9bd0ff', dark: '#2878c7' },
    secondary: { main: '#9b8cff' },
    success: { main: '#42c99a' },
    warning: { main: '#f4b860' },
    error: { main: '#ff727c' },
    background: { default: '#080f1b', paper: '#101c2d' },
    text: { primary: '#edf4ff', secondary: '#91a3bb' },
    divider: 'rgba(157,184,218,0.13)',
  },
  shape: { borderRadius: 16 },
  typography: {
    fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    h3: { fontWeight: 800, letterSpacing: '-0.045em' },
    h4: { fontWeight: 750, letterSpacing: '-0.035em' },
    h5: { fontWeight: 750, letterSpacing: '-0.025em' },
    h6: { fontWeight: 700, letterSpacing: '-0.015em' },
    button: { textTransform: 'none', fontWeight: 700 },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundImage: 'radial-gradient(ellipse at 12% 0%, rgba(42,112,190,.13), transparent 34%), radial-gradient(ellipse at 90% 10%, rgba(113,85,190,.10), transparent 30%)',
          backgroundAttachment: 'fixed',
        },
        '*': { scrollbarWidth: 'thin', scrollbarColor: '#33465f transparent' },
      },
    },
    MuiPaper: { styleOverrides: { root: { backgroundImage: 'none', border: '1px solid rgba(157,184,218,0.12)' } } },
    MuiCard: { styleOverrides: { root: { backgroundImage: 'linear-gradient(145deg, rgba(20,36,56,.96), rgba(13,25,41,.96))', border: '1px solid rgba(157,184,218,0.13)', boxShadow: '0 18px 50px rgba(0,0,0,.16)' } } },
    MuiButton: { styleOverrides: { root: { borderRadius: 11, paddingInline: 18 } } },
    MuiTextField: { defaultProps: { fullWidth: true, size: 'medium' } },
  },
});
