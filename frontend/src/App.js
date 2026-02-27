import React, { useState } from 'react';
import Upload from './components/Upload';
import Result from './components/Result';
import StatusBar from './components/StatusBar';
import { processClaim, extractOnly, generateFhirBundle, validateFhirBundle, getBundleSummary } from './api/claimService';

export const T = {
  p1: '#4f46e5',
  p2: '#4338ca',
  p3: '#e0e7ff',
  a1: '#ec4899',
  a2: '#db2777',
  s1: '#0ea5e9',
  w1: '#f59e0b',
  g1: '#10b981',
  er: '#ef4444',

  gradBrand: 'linear-gradient(135deg, #4f46e5 0%, #4338ca 40%, #0ea5e9 100%)',
  gradBtn: 'linear-gradient(135deg, #4f46e5 0%, #4338ca 100%)',
  gradStripe: 'linear-gradient(90deg, #4f46e5 0%, #0ea5e9 40%, #ec4899 100%)',

  bg: '#f8fafc',
  bgPanel: '#ffffff',
  bgSidebar: '#ffffff',
  border: '#e2e8f0',
  borderGrey: '#e5e7eb',

  text: '#0f172a',
  textSub: '#334155',
  textDim: '#64748b',
};

export default function App() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [isGeneratingFhir, setIsGeneratingFhir] = useState(false);
  const [resultData, setResultData] = useState(null);
  const [error, setError] = useState('');
  const [fileName, setFileName] = useState('');
  const [shouldGenerateFhir, setShouldGenerateFhir] = useState(true);
  const [summary, setSummary] = useState(null);
  const [validation, setValidation] = useState(null);

  const reset = () => { setResultData(null); setError(''); setSummary(null); setValidation(null); };

  const enrichBundle = async (b) => {
    try {
      const [s, v] = await Promise.all([getBundleSummary(b).catch(() => null), validateFhirBundle(b).catch(() => null)]);
      setSummary(s); setValidation(v);
    } catch { }
  };

  const handleProcess = async (file) => {
    if (!file) { setError('Please select a file first.'); return; }
    setIsProcessing(true); reset(); setFileName(file.name);
    try { const r = await processClaim(file, shouldGenerateFhir); setResultData(r); if (r.fhir_bundle) await enrichBundle(r.fhir_bundle); }
    catch (e) { setError(e.message || 'Unknown error'); }
    finally { setIsProcessing(false); }
  };

  const handleExtractOnly = async (file) => {
    if (!file) { setError('Please select a file first.'); return; }
    setIsProcessing(true); reset(); setFileName(file.name);
    try { setResultData(await extractOnly(file)); }
    catch (e) { setError(e.message || 'Unknown error'); }
    finally { setIsProcessing(false); }
  };

  const handleGenerateFhir = async () => {
    if (!resultData?.extracted_data) return;
    setIsGeneratingFhir(true); setError('');
    try {
      const fb = await generateFhirBundle(resultData.extracted_data);
      setResultData({ ...resultData, fhir_bundle: fb });
      await enrichBundle(fb);
    } catch (e) { setError(e.message || 'Failed to generate FHIR'); }
    finally { setIsGeneratingFhir(false); }
  };

  return (
    <div className="main-wrapper" style={{ height: '100vh', background: T.bg, fontFamily: "'Inter', sans-serif", color: T.text, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

      <header style={{
        padding: '0 24px', height: 62, minHeight: 62, flexShrink: 0,
        display: 'flex', alignItems: 'center', gap: 14,
        background: '#ffffff',
        borderBottom: `1px solid ${T.border}`,
        boxShadow: '0 1px 8px rgba(16,185,129,0.08)',
        zIndex: 100, position: 'relative',
      }}>
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: T.gradStripe }} />

        <div style={{
          width: 36, height: 36, borderRadius: 10, flexShrink: 0,
          background: T.gradBtn,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 4px 14px rgba(16,185,129,0.4)',
          animation: 'emeraldGlow 3s ease-in-out infinite',
        }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
              stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>

        <div>
          <div style={{ fontSize: 15, fontWeight: 900, letterSpacing: -0.4, lineHeight: 1.1 }}>
            <span style={{ background: T.gradBrand, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>NHCX FHIR</span>
            {' '}<span style={{ color: T.text }}>Utility</span>
          </div>
          <div style={{ fontSize: 10, color: T.textDim, letterSpacing: 0.7, textTransform: 'uppercase', fontWeight: 500 }}>Insurance Claim Processor</div>
        </div>

        <div style={{ flex: 1 }} />
        <div className="header-actions">
          <StatusBar busy={isProcessing || isGeneratingFhir} />
        </div>
      </header>

      <div className="app-layout" style={{ flex: 1, minHeight: 0, overflow: 'hidden' }}>

        <aside className="sidebar-container" style={{
          padding: 20, background: '#ffffff',
          display: 'flex', flexDirection: 'column', overflow: 'auto',
        }}>
          <Upload
            onProcess={handleProcess} onExtractOnly={handleExtractOnly}
            isProcessing={isProcessing} shouldGenerateFhir={shouldGenerateFhir}
            onFhirToggleChange={(e) => setShouldGenerateFhir(e.target.checked)}
          />

          <div style={{ marginTop: 'auto', paddingTop: 20 }}>
            <div style={{ fontSize: 10, color: T.textDim, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 10, fontWeight: 700 }}>Pipeline</div>
            {[
              { icon: '📄', label: 'PDF → OCR', desc: 'Marker ML model', color: T.s1 },
              { icon: '🤖', label: 'OCR → JSON', desc: 'LLM extraction', color: T.p1 },
              { icon: '⚕️', label: 'JSON → FHIR', desc: 'R4 mapper', color: T.a1 },
            ].map(({ icon, label, desc, color }) => (
              <div key={label} style={{
                display: 'flex', alignItems: 'center', gap: 10, padding: '8px 10px',
                borderRadius: 10, marginBottom: 5,
                background: `${color}0a`, border: `1px solid ${color}22`,
              }}>
                <span style={{ fontSize: 14 }}>{icon}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 11, color, fontWeight: 700 }}>{label}</div>
                  <div style={{ fontSize: 10, color: T.textDim }}>{desc}</div>
                </div>
                <div style={{ width: 6, height: 6, borderRadius: '50%', background: color, boxShadow: `0 0 5px ${color}88` }} />
              </div>
            ))}
          </div>
        </aside>

        <section style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden', background: '#f8fafc', minWidth: 0 }}>
          <Result
            isProcessing={isProcessing} data={resultData} error={error} fileName={fileName}
            onGenerateFhir={handleGenerateFhir} isGeneratingFhir={isGeneratingFhir}
            summary={summary} validation={validation}
          />
        </section>
      </div>
    </div>
  );
}