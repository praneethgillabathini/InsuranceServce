import React, { useState } from 'react';

const P1 = '#4f46e5'; const P2 = '#4338ca';
const A1 = '#ec4899'; const S1 = '#0ea5e9';
const W1 = '#f59e0b'; const ER = '#ef4444';

const Tag = ({ children, color }) => (
    <span style={{ display: 'inline-flex', alignItems: 'center', padding: '3px 10px', borderRadius: 20, fontSize: 11, fontWeight: 700, background: `${color}12`, color, border: `1px solid ${color}30`, whiteSpace: 'nowrap' }}>{children}</span>
);

const Stat = ({ label, value, color, icon, onClick, active }) => (
    <div
        onClick={onClick}
        style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center',
            padding: '12px 14px', borderRadius: 14, minWidth: 72,
            background: active ? `${color}22` : `${color}0c`,
            border: `1px solid ${active ? color : `${color}22`}`,
            cursor: onClick ? 'pointer' : 'default',
            transition: 'all 0.2s ease',
            transform: active ? 'scale(1.02)' : 'scale(1)'
        }}
    >
        <span style={{ fontSize: 20, fontWeight: 900, color, lineHeight: 1 }}>{value}</span>
        <span style={{ fontSize: 9, color: '#9ca3af', marginTop: 4, textTransform: 'uppercase', letterSpacing: 0.5 }}>{icon} {label}</span>
    </div>
);

export default function SummaryCard({ summary, validation }) {
    const [activeDetail, setActiveDetail] = useState(null);

    if (!summary) return null;
    const statusColor = summary.status === 'active' ? P1 : W1;

    const detailsMap = {
        coverages: summary.coverageNames?.length ? summary.coverageNames.join(', ') : 'No specific coverages listed',
        benefits: summary.benefitNames?.length ? summary.benefitNames.join(', ') : 'No specific benefits listed',
        plans: summary.planNames?.length ? summary.planNames.join(', ') : 'No specific plans listed',
        exclusions: summary.exclusionNames?.length ? summary.exclusionNames.join(', ') : 'No specific exclusions listed'
    };

    return (
        <div style={{ borderRadius: 18, background: '#ffffff', border: '1px solid #e2e8f0', padding: 20, marginBottom: 14, boxShadow: '0 4px 20px rgba(79,70,229,0.1)', position: 'relative', overflow: 'hidden', animation: 'vfadein 0.3s ease' }}>
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: 'linear-gradient(90deg, #4f46e5, #0ea5e9, #ec4899)' }} />

            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
                <div style={{ flex: 1, marginRight: 12 }}>
                    <div style={{ fontSize: 18, fontWeight: 800, color: '#0f172a', marginBottom: 8, letterSpacing: -0.3 }}>{summary.planName}</div>
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        <Tag color={statusColor}>{summary.status}</Tag>
                        {summary.planType && <Tag color={S1}>{summary.planType}</Tag>}
                        {summary.language && <Tag color={P1}>{summary.language}</Tag>}
                        {(summary.alias || []).map(a => <Tag key={a} color={W1}>{a}</Tag>)}
                    </div>
                </div>
                {validation && (
                    <div style={{ padding: '7px 14px', borderRadius: 10, flexShrink: 0, background: validation.valid ? '#e0e7ff' : '#fce7f3', border: `1px solid ${validation.valid ? '#c7d2fe' : '#fbcfe8'}`, color: validation.valid ? P2 : A1, fontWeight: 800, fontSize: 12, textAlign: 'center' }}>
                        {validation.valid ? '✓ Valid' : `✗ ${validation.issue_count} Issues`}
                        <div style={{ fontSize: 9, opacity: 0.6, fontWeight: 400, marginTop: 1 }}>FHIR R4</div>
                    </div>
                )}
            </div>

            <div style={{ display: 'flex', gap: 24, marginBottom: 14, fontSize: 12, flexWrap: 'wrap' }}>
                {[
                    { label: 'Insurer', value: summary.insurer, color: S1 },
                    summary.tpa && { label: 'TPA', value: summary.tpa, color: P1 },
                    summary.period?.start && { label: 'Period', value: `${summary.period.start} → ${summary.period.end}`, color: A1 },
                ].filter(Boolean).map(({ label, value, color }) => (
                    <div key={label}>
                        <div style={{ fontSize: 10, color: '#64748b', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 1 }}>{label}</div>
                        <div style={{ color, fontWeight: 700 }}>{value}</div>
                    </div>
                ))}
            </div>

            {summary.networks?.length > 0 && (
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center', marginBottom: 14 }}>
                    <span style={{ fontSize: 10, color: '#64748b', textTransform: 'uppercase', letterSpacing: 0.5 }}>Networks:</span>
                    {summary.networks.map(n => <Tag key={n} color={S1}>{n}</Tag>)}
                </div>
            )}

            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                <Stat label='Coverages' value={summary.coverageCount} color={P1} icon='🛡' onClick={() => setActiveDetail(activeDetail === 'coverages' ? null : 'coverages')} active={activeDetail === 'coverages'} />
                <Stat label='Benefits' value={summary.benefitCount} color={A1} icon='💊' onClick={() => setActiveDetail(activeDetail === 'benefits' ? null : 'benefits')} active={activeDetail === 'benefits'} />
                <Stat label='Plans' value={summary.planCount} color={S1} icon='📋' onClick={() => setActiveDetail(activeDetail === 'plans' ? null : 'plans')} active={activeDetail === 'plans'} />
                <Stat label='Exclusions' value={summary.exclusionCount} color={W1} icon='⛔' onClick={() => setActiveDetail(activeDetail === 'exclusions' ? null : 'exclusions')} active={activeDetail === 'exclusions'} />
                <Stat label='Resources' value={summary.totalResources} color={P2} icon='🔗' />
            </div>

            {activeDetail && (
                <div style={{
                    marginTop: 12, padding: '10px 14px', borderRadius: 10,
                    background: '#f8fafc', border: '1px solid #e2e8f0',
                    fontSize: 12, color: '#475569',
                    animation: 'vfadein 0.2s ease',
                    boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.02)'
                }}>
                    <strong style={{ color: '#0f172a', textTransform: 'capitalize' }}>{activeDetail}:</strong> {detailsMap[activeDetail]}
                </div>
            )}

            {validation && !validation.valid && (
                <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid #e2e8f0' }}>
                    <div style={{ fontSize: 11, color: '#64748b', marginBottom: 8, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.5 }}>FHIR Issues</div>
                    {validation.issues.map((issue, i) => (
                        <div key={i} style={{ display: 'flex', gap: 8, fontSize: 11, padding: '5px 0', borderBottom: '1px solid #f8fafc', alignItems: 'center' }}>
                            <Tag color={issue.severity === 'error' ? ER : issue.severity === 'warning' ? W1 : P1}>{issue.severity}</Tag>
                            <span style={{ color: '#64748b', fontFamily: 'monospace', fontSize: 10 }}>{issue.field}</span>
                            <span style={{ color: '#94a3b8' }}>{issue.message}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
