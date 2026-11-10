import { useState } from 'react';
import { Alert, Button, Card, CardContent, Container, Stack, TextField, Typography } from '@mui/material';
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
      nav(`/workflows/${result.thread_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to start workflow. Check browser console for details.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <Container sx={{ py: 4 }}>
      <Card>
        <CardContent>
          <Typography variant="h4">AKS Upgrade Agent</Typography>
          <Stack spacing={2} mt={2}>
            {error && <Alert severity="error">{error}</Alert>}
            <TextField label="Resource group" value={form.resource_group} onChange={e => setForm({ ...form, resource_group: e.target.value })} />
            <TextField label="AKS cluster" value={form.cluster_name} onChange={e => setForm({ ...form, cluster_name: e.target.value })} />
            <TextField label="Target version" value={form.target_version} onChange={e => setForm({ ...form, target_version: e.target.value })} />
            <Button onClick={() => setForm({ ...form, dry_run: !form.dry_run })}>
              {form.dry_run ? 'Dry run enabled' : 'Real upgrade requested'}
            </Button>
            <Typography variant="body2" color="text.secondary">
              {form.dry_run ? 'No cluster changes will be applied.' : 'This requests a real upgrade, subject to backend safety checks and approval.'}
            </Typography>
            <Button variant="contained" onClick={submit} disabled={loading}>
              {loading ? 'Starting workflow…' : 'Start workflow'}
            </Button>
          </Stack>
        </CardContent>
      </Card>
    </Container>
  );
}
