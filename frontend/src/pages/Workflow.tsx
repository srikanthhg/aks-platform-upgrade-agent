import { useCallback, useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { Alert, Box, Button, Chip, Container, Dialog, DialogActions, DialogContent, DialogTitle, Grid, Paper, Stack, TextField, Typography } from '@mui/material';
import { ArrowBack, CheckCircleOutline, Refresh } from '@mui/icons-material';
import { api } from '../api';
import type { WorkflowResponse } from '../types';
import { StatusChip } from '../components/StatusChip';
import { WorkflowTimeline } from '../components/WorkflowTimeline';

export default function Workflow() {
  const { id = '' } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [data, setData] = useState<WorkflowResponse | undefined>(location.state as WorkflowResponse);
  const [error, setError] = useState('');
  const [comment, setComment] = useState('');
  const [dialog, setDialog] = useState<'approve' | 'reject' | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      const result = await api.get(id);
      setData(result);
      setError('');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to load workflow status.');
    }
  }, [id]);

  useEffect(() => {
    void load();
    const timer = setInterval(() => { void load(); }, 5000);
    return () => clearInterval(timer);
  }, [load]);

  async function decide(approved: boolean) {
    try {
      setData(await api.decide(id, approved, comment));
      setDialog(null);
      setComment('');
      setError('');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to submit the decision.');
    }
  }

  async function refresh() {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  }

  if (!data) {
    return <Container maxWidth="lg" sx={{ py: 6 }}>
      <Stack spacing={2}><Typography variant="h5">Loading workflow</Typography>
        {error ? <Alert severity="error">{error}</Alert> : <Typography color="text.secondary">Connecting to the workflow service…</Typography>}
        <Button startIcon={<ArrowBack />} onClick={() => navigate('/')}>Back to dashboard</Button>
      </Stack>
    </Container>;
  }

  const interrupt = data.interrupt?.[0] as Record<string, unknown> | undefined;
  const clusterName = String(interrupt?.cluster_name ?? data.state.cluster?.cluster_name ?? 'AKS cluster');
  const targetVersion = String(interrupt?.target_version ?? data.state.upgrade?.target_version ?? 'requested version');
  const isRealUpgrade = interrupt?.dry_run === false;

  return (
    <Container maxWidth="xl" sx={{ py: { xs: 3, md: 5 } }}>
      <Stack spacing={3}>
        <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }} gap={2}>
          <Box>
            <Button startIcon={<ArrowBack />} onClick={() => navigate('/')} sx={{ mb: 1, px: 0 }}>Dashboard</Button>
            <Typography variant="h4">Upgrade workflow</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: .5 }}>Track execution, review progress and respond to approval requests.</Typography>
          </Box>
          <Stack direction="row" spacing={1} alignItems="center">
            <StatusChip status={data.status} />
            <Button variant="outlined" startIcon={<Refresh />} onClick={refresh} disabled={refreshing}>Refresh</Button>
          </Stack>
        </Stack>

        {error && <Alert severity="error">{error}</Alert>}

        <Grid container spacing={2}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2.5, height: '100%' }}>
              <Typography variant="overline" color="text.secondary">WORKFLOW IDENTIFIER</Typography>
              <Typography sx={{ fontFamily: 'monospace', overflowWrap: 'anywhere' }}>{id}</Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mt: 2 }}>
                <Chip label={clusterName} variant="outlined" />
                <Chip label={`Target ${targetVersion}`} variant="outlined" color="primary" />
                <Chip label={isRealUpgrade ? 'Real upgrade' : 'Dry run'} color={isRealUpgrade ? 'warning' : 'success'} variant="outlined" />
              </Stack>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2.5, height: '100%' }}>
              <Typography variant="overline" color="text.secondary">CURRENT STATUS</Typography>
              <Typography variant="h5" sx={{ mt: .5, textTransform: 'capitalize' }}>{data.status.replaceAll('_', ' ').toLowerCase()}</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>Status refreshes automatically every five seconds.</Typography>
            </Paper>
          </Grid>
        </Grid>

        {data.paused && (
          <Alert severity="warning" action={<Stack direction="row" spacing={1}>
            <Button color="inherit" onClick={() => setDialog('reject')}>Reject</Button>
            <Button color="inherit" variant="outlined" onClick={() => setDialog('approve')}>Approve</Button>
          </Stack>}>
            <Typography fontWeight={700}>Operator approval required</Typography>
            Review the plan for {clusterName} targeting {targetVersion}. {isRealUpgrade ? 'This is a REAL upgrade.' : 'This is a dry run.'}
            {interrupt?.plan_hash ? ` Plan fingerprint: ${String(interrupt.plan_hash).slice(0, 16)}…` : ''}
          </Alert>
        )}

        <WorkflowTimeline state={data.state} status={data.status} />

        <Paper sx={{ p: 2.5 }}>
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1.5 }}>
            <CheckCircleOutline color="primary" />
            <Typography variant="h6">Execution details</Typography>
          </Stack>
          <Box component="pre" sx={{ m: 0, p: 2, borderRadius: 2, bgcolor: '#080f1b', color: '#c7d8ed', overflow: 'auto', fontSize: 12, lineHeight: 1.6 }}>
            {JSON.stringify(data.state, null, 2)}
          </Box>
        </Paper>
      </Stack>

      <Dialog open={dialog !== null} onClose={() => setDialog(null)} fullWidth maxWidth="sm">
        <DialogTitle>{dialog === 'approve' ? 'Approve upgrade plan' : 'Reject upgrade plan'}</DialogTitle>
        <DialogContent>
          <Typography color="text.secondary" variant="body2" sx={{ mb: 2 }}>Add an audit comment explaining your decision.</Typography>
          <TextField multiline minRows={3} label="Operator comment" value={comment} onChange={e => setComment(e.target.value)} />
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setDialog(null)}>Cancel</Button>
          <Button variant="contained" color={dialog === 'approve' ? 'success' : 'error'} onClick={() => decide(dialog === 'approve')} disabled={!comment.trim()}>
            Confirm {dialog === 'approve' ? 'approval' : 'rejection'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
