import React, { useEffect, useRef, useState } from 'react';
import { getServiceHealth } from '../api/claimService';

export default function StatusBar({ busy = false }) {
    const [health, setHealth] = useState(null);
    const busyRef = useRef(busy);

    useEffect(() => { busyRef.current = busy; }, [busy]);

    useEffect(() => {
        let cancelled = false;

        const poll = async () => {
            if (busyRef.current) return;
            try {
                const d = await getServiceHealth();
                if (!cancelled) setHealth(d);
            } catch {
                if (!cancelled) setHealth({ status: 'unreachable' });
            }
        };

        poll();
        const id = setInterval(poll, 30000);
        return () => { cancelled = true; clearInterval(id); };
    }, []);

    const overall = health?.status ?? 'loading';
    const cfg = {
        healthy: { color: '#059669', bg: '#ecfdf5', border: '#a7f3d0', label: 'Healthy' },
        degraded: { color: '#d97706', bg: '#fffbeb', border: '#fde68a', label: 'Degraded' },
        unreachable: { color: '#e11d48', bg: '#fff1f2', border: '#fecdd3', label: 'Offline' },
        loading: { color: '#4f46e5', bg: '#e0e7ff', border: '#c7d2fe', label: busy ? 'Busy…' : 'Checking…' },
    };
    const { color, bg, border, label } = cfg[overall] ?? cfg.loading;
    const compColors = ['#0ea5e9', '#4f46e5', '#ec4899', '#f59e0b'];

    return (
        <div style={{
            display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap',
            padding: '5px 12px', borderRadius: 10, fontSize: 11,
            background: '#f9fafb', border: '1px solid #e5e7eb',
        }}>
            <span style={{
                display: 'inline-flex', alignItems: 'center', gap: 5,
                padding: '3px 9px', borderRadius: 8,
                background: bg, border: `1px solid ${border}`, color, fontWeight: 700,
            }}>
                <span style={{
                    width: 6, height: 6, borderRadius: '50%', background: color,
                    display: 'inline-block', boxShadow: `0 0 5px ${color}88`,
                    animation: busy ? 'pulse 1s ease-in-out infinite' : 'none',
                }} />
                {busy ? 'Processing…' : `API ${label}`}
            </span>

            {!busy && health?.components && Object.entries(health.components).map(([key, val], i) => (
                <span key={key} style={{ display: 'flex', alignItems: 'center', gap: 4, color: '#6b7280', fontSize: 10 }}>
                    <span style={{ width: 5, height: 5, borderRadius: '50%', display: 'inline-block', background: val.status === 'ok' ? compColors[i % compColors.length] : '#e11d48' }} />
                    {key.replace('_', ' ')}
                </span>
            ))}

            {health?.api_version && (
                <span style={{ fontSize: 9, fontWeight: 700, padding: '1px 6px', borderRadius: 5, background: '#d1fae5', color: '#065f46', letterSpacing: 0.5, marginLeft: 2 }}>
                    v{health.api_version}
                </span>
            )}
        </div>
    );
}
