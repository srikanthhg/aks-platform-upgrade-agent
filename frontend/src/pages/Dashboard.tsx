import { useState } from 'react';
import { Alert, Box, Button, Card, CardContent, Chip, Container, FormControlLabel, Grid, Stack, Switch, TextField, Typography } from '@mui/material';
import { ArrowForward, AutoAwesome, CloudQueue, Security, Speed, Terminal } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import type { StartPayload } from '../types';

const initial: StartPayload = {
  resource_group: '',
  cluster_name: '',
  target_version: '',
  subscription_id: '',
  dry_run: true,
  max_surge: '33%',
};

function Feature({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <Stack direction="row" spacing={1.5} alignItems="flex-start">
      <Box sx={{ color: 'primary.main', p: 1, bgcolor: 'rgba(102,179,255,.10)', borderRadius: 2, display: 'flex' }}>{icon}</Box>
      <Box><Typography fontWeight={700}>{title}</Typography><Typography variant="body2" color="text.secondary">{description}</Typography></Box>
    </Stack>
  );
}

export default function Dashboard() {
  const nav = useNavigate();
  const [form, setForm] = useState(initial);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function submit() {
    if (loading) return;
    setError('');
    setLoading(true);
    try {
      const result = await api.start(form);
      nav(`/workflows/${result.thread_id}`, { state: result });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to start workflow. Check browser console for details.');
    } finally {
      setLoading(false);
    }
  }

  const update = (field: keyof StartPayload, value: string | boolean) => setForm(current => ({ ...current, [field]: value }));

  return (
    <Container maxWidth="xl" sx={{ py: { xs: 4, md: 7 } }}>
      <Stack spacing={4}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 2, flexWrap: 'wrap' }}>
          <Box>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
              <Chip icon={<AutoAwesome />} label="INTELLIGENT UPGRADE ORCHESTRATION" size="small" color="primary" variant="outlined" />
              <Chip label="CONTROL PLANE + NODEPOOLS" size="small" variant="outlined" />
            </Stack>
            <Typography variant="h3" sx={{ fontSize: { xs: 34, md: 46 } }}>Kubernetes, <Box component="span" sx={{ color: 'primary.light' }}>under control.</Box></Typography>
            <Typography color="text.secondary" sx={{ mt: 1, maxWidth: 650 }}>Prepare a safe AKS upgrade with discovery, compatibility validation, operator approval and post-upgrade checks.</Typography>
          </Box>
          <Chip icon={<Security />} label="Entra ID secured" color="success" variant="outlined" />
        </Box>

        <Grid container spacing={2}>
          {[
            { icon: <CloudQueue />, title: 'Discover', text: 'Inspect cluster and nodepool versions' },
            { icon: <Security />, title: 'Validate', text: 'Check upgrade readiness and safety' },
            { icon: <Speed />, title: 'Orchestrate', text: 'Control-plane-first upgrade sequence' },
          ].map(item => (
            <Grid item xs={12} md={4} key={item.title}>
              <Card sx={{ height: '100%' }}><CardContent sx={{ display: 'flex', gap: 2, alignItems: 'center', p: 2.5 }}>
                <Box sx={{ p: 1.5, display: 'flex', borderRadius: 3, color: 'primary.light', bgcolor: 'rgba(102,179,255,.10)' }}>{item.icon}</Box>
                <Box><Typography fontWeight={750}>{item.title}</Typography><Typography variant="body2" color="text.secondary">{item.text}</Typography></Box>
              </CardContent></Card>
            </Grid>
          ))}
        </Grid>

        <Grid container spacing={3} alignItems="stretch">
          <Grid item xs={12} md={7}>
            <Card sx={{ height: '100%' }}>
              <CardContent sx={{ p: { xs: 2.5, md: 3.5 } }}>
                <Stack spacing={2.5}>
                  <Box>
                    <Typography variant="h5">Configure upgrade</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: .5 }}>Enter the target AKS cluster and desired Kubernetes version.</Typography>
                  </Box>
                  {error && <Alert severity="error">{error}</Alert>}
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}><TextField label="Resource group" placeholder="e.g. rg-platform-prod" value={form.resource_group} onChange={e => update('resource_group', e.target.value)} /></Grid>
                    <Grid item xs={12} sm={6}><TextField label="AKS cluster name" placeholder="e.g. aks-prod-eastus" value={form.cluster_name} onChange={e => update('cluster_name', e.target.value)} /></Grid>
                    <Grid item xs={12} sm={6}><TextField label="Target Kubernetes version" placeholder="e.g. 1.32.4" value={form.target_version} onChange={e => update('target_version', e.target.value)} /></Grid>
                    <Grid item xs={12} sm={6}><TextField label="Subscription ID (optional)" placeholder="Azure subscription ID" value={form.subscription_id} onChange={e => update('subscription_id', e.target.value)} /></Grid>
                    <Grid item xs={12}><TextField label="Maximum surge" value={form.max_surge} onChange={e => update('max_surge', e.target.value)} helperText="Nodepool upgrade surge setting (default: 33%)." /></Grid>
                  </Grid>
                  <Box sx={{ p: 2, borderRadius: 3, bgcolor: 'rgba(102,179,255,.06)', border: 1, borderColor: 'divider' }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" gap={2}>
                      <Box><Typography fontWeight={700}>Dry-run mode</Typography><Typography variant="body2" color="text.secondary">Validate and prepare without applying cluster changes.</Typography></Box>
                      <FormControlLabel sx={{ m: 0 }} control={<Switch checked={form.dry_run} onChange={e => update('dry_run', e.target.checked)} color="success" />} label={form.dry_run ? 'Enabled' : 'Disabled'} />
                    </Stack>
                    {!form.dry_run && <Alert severity="warning" sx={{ mt: 2 }}>A real upgrade is requested. Backend safety checks and operator approval still apply.</Alert>}
                  </Box>
                  <Button size="large" variant="contained" endIcon={<ArrowForward />} onClick={submit} disabled={loading || !form.resource_group || !form.cluster_name || !form.target_version}>
                    {loading ? 'Starting workflow…' : 'Start upgrade workflow'}
                  </Button>
                  <Typography variant="caption" color="text.secondary">Starting a workflow does not bypass validation or required approval gates.</Typography>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={5}>
            <Card sx={{ height: '100%' }}>
              <CardContent sx={{ p: 3.5 }}>
                <Stack spacing={3}>
                  <Box><Chip label="BUILT FOR PLATFORM TEAMS" size="small" color="secondary" variant="outlined" /><Typography variant="h5" sx={{ mt: 1.5 }}>Upgrade with confidence</Typography><Typography color="text.secondary" variant="body2" sx={{ mt: 1 }}>A guided workflow keeps each stage visible and puts operators in control of production changes.</Typography></Box>
                  <Feature icon={<CloudQueue />} title="Cluster discovery" description="Gather cluster, nodepool and version details." />
                  <Feature icon={<Security />} title="Safety-first approvals" description="Review the upgrade plan before execution." />
                  <Feature icon={<Speed />} title="Ordered execution" description="Upgrade control plane before worker nodepools." />
                  <Feature icon={<Terminal />} title="Post-upgrade verification" description="Validate cluster health and report the outcome." />
                  <Box sx={{ p: 2, bgcolor: 'rgba(155,140,255,.08)', borderRadius: 3 }}>
                    <Typography variant="body2" fontWeight={700}>Operational principle</Typography>
                    <Typography variant="body2" color="text.secondary">No silent production changes. Every real upgrade follows validation and the configured approval process.</Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Stack>
    </Container>
  );
}
