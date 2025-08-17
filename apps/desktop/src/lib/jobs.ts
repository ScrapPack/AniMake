export async function runStage(stage: string, shotId: string) {
  const r = await fetch(`http://localhost:5175/run/${stage}/${shotId}`, { method: 'POST' });
  if (!r.ok) throw new Error('run failed');
  return (await r.json()).job_id as string;
}

export function openJobWS(jobId: string, onMsg: (e: { pct: number; msg: string }) => void) {
  const ws = new WebSocket(`ws://localhost:5175/jobs/${jobId}/logs`);
  ws.onmessage = (ev) => {
    onMsg(JSON.parse(ev.data));
  };
  return ws;
}

export async function getJob(jobId: string) {
  const r = await fetch(`http://localhost:5175/jobs/${jobId}`);
  return r.json();
}


