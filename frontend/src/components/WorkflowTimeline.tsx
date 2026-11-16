import { CheckCircle, RadioButtonUnchecked } from '@mui/icons-material';
import { Box, LinearProgress, Paper, Stack, Typography } from '@mui/material';

const steps = ['discovery', 'validation', 'approval', 'upgrade', 'post-validation', 'reporting'];

export function WorkflowTimeline({ state, status }: { state: Record<string, any>; status: string }) {
  const current = String(state.workflow?.current_step ?? '').toLowerCase().replaceAll('_', '-');
  const activeIndex = current.includes('worker-queue') || !current ? 0 : steps.findIndex(step => current.includes(step));
  const finished = ['completed', 'success', 'succeeded'].includes(status.toLowerCase());

  return (
    <Paper sx={{ p: { xs: 2.5, md: 3 }, borderRadius: 3 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2.5 }}>
        <Box><Typography variant="h6">Workflow progress</Typography><Typography variant="body2" color="text.secondary">Live execution stages</Typography></Box>
        <Typography variant="caption" color="text.secondary">{finished ? 'All stages complete' : current.replaceAll('-', ' ') || 'Queued'}</Typography>
      </Stack>
      <Stack spacing={1.5}>
        {steps.map((step, index) => {
          const complete = finished || (activeIndex > index && activeIndex >= 0);
          const active = !finished && index === Math.max(activeIndex, 0);
          return (
            <Box key={step} sx={{ display: 'flex', gap: 1.5, alignItems: 'center' }}>
              {complete ? <CheckCircle color="success" /> : <RadioButtonUnchecked color={active ? 'primary' : 'disabled'} />}
              <Box sx={{ flex: 1 }}>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography sx={{ textTransform: 'capitalize', fontWeight: active || complete ? 700 : 500, color: active ? 'primary.light' : complete ? 'text.primary' : 'text.secondary' }}>{step.replaceAll('-', ' ')}</Typography>
                  <Typography variant="caption" color={complete ? 'success.main' : active ? 'primary.light' : 'text.disabled'}>{complete ? 'Complete' : active ? 'In progress' : 'Pending'}</Typography>
                </Stack>
                {active && <LinearProgress sx={{ mt: .75, height: 4, borderRadius: 5 }} />}
              </Box>
            </Box>
          );
        })}
      </Stack>
    </Paper>
  );
}
