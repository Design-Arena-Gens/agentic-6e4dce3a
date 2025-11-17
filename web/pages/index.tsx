import { useEffect, useState } from 'react';

type SessionResult = {
  session_id: string;
  ok: boolean;
  strategy: string;
  results: Array<{
    url: string;
    ok: boolean;
    strategy: string;
    html?: string | null;
    text_len?: number;
    title?: string;
    error?: string;
  }>;
};

type Summary = {
  ok: boolean;
  concurrent_sessions: number;
  sessions: SessionResult[];
  output_dir: string;
};

export default function Home() {
  const [data, setData] = useState<Summary | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    fetch('/data.json')
      .then(r => r.json())
      .then(setData)
      .catch(err => setError(String(err)));
  }, []);

  return (
    <main style={{ maxWidth: 960, margin: '40px auto', padding: 20, fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial' }}>
      <h1>St Kilda 3182 Scrape Sessions</h1>
      {error && <p style={{ color: 'crimson' }}>{error}</p>}
      {!data && !error && <p>Loading?</p>}
      {data && (
        <div>
          <p><strong>Overall success:</strong> {data.ok ? '? OK' : '? Blocked'}</p>
          <p><strong>Concurrent sessions:</strong> {data.concurrent_sessions}</p>
          <p><strong>Artifacts:</strong> {data.output_dir}</p>
          {data.sessions.map((s) => (
            <div key={s.session_id} style={{ border: '1px solid #ddd', borderRadius: 8, padding: 16, marginTop: 16 }}>
              <h3>Session {s.session_id} ({s.strategy}) ? {s.ok ? '?' : '?'}</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: '8px 4px' }}>#</th>
                    <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: '8px 4px' }}>URL</th>
                    <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: '8px 4px' }}>Title</th>
                    <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: '8px 4px' }}>Text len</th>
                    <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: '8px 4px' }}>OK</th>
                    <th style={{ textAlign: 'left', borderBottom: '1px solid #eee', padding: '8px 4px' }}>Error</th>
                  </tr>
                </thead>
                <tbody>
                  {s.results.map((r, idx) => (
                    <tr key={idx}>
                      <td style={{ padding: '6px 4px', borderBottom: '1px solid #f3f3f3' }}>{idx + 1}</td>
                      <td style={{ padding: '6px 4px', borderBottom: '1px solid #f3f3f3', maxWidth: 320, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={r.url}>{r.url}</td>
                      <td style={{ padding: '6px 4px', borderBottom: '1px solid #f3f3f3' }}>{r.title || ''}</td>
                      <td style={{ padding: '6px 4px', borderBottom: '1px solid #f3f3f3' }}>{r.text_len ?? 0}</td>
                      <td style={{ padding: '6px 4px', borderBottom: '1px solid #f3f3f3' }}>{r.ok ? '?' : '?'}</td>
                      <td style={{ padding: '6px 4px', borderBottom: '1px solid #f3f3f3', color: '#a33' }}>{r.error || ''}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
