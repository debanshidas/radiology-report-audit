/* ═══════════════════════════════════════════════════════════════════
   AI Radiology Report Audit — app.js
   Full SPA logic: navigation, file upload, API calls, rendering
   ═══════════════════════════════════════════════════════════════════ */

'use strict';

// 💡 PASTE YOUR DEFAULT API KEY BELOW TO AUTO-LOAD IT ON THE WEBSITE:
const DEFAULT_API_KEY = "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"; // Paste your Groq (gsk_...) or Gemini (AIza...) key inside quotes
const DEFAULT_PROVIDER = "groq"; // 'groq' or 'gemini'

// ── App State ──────────────────────────────────────────────────────────────
const App = {
  provider: DEFAULT_PROVIDER,
  apiKey: DEFAULT_API_KEY,
  reportText: '',
  reportFilename: '',
  modality: 'Chest X-Ray',
  mandatorySections: [],
  auditResult: null,
  auditTimestamp: null,
  reportsAnalyzed: 0,
  reportsExported: 0,
};

// ── Modality Sections ──────────────────────────────────────────────────────
const MODALITY_SECTIONS = {
  'Chest X-Ray': [
    'Patient Demographics', 'Clinical Indication / History', 'Comparison Study',
    'Procedure Details / Technique', 'Findings (Lungs, Heart, Pleura, Bones)',
    'Impression / Conclusion', 'Reporting Radiologist Signature',
  ],
  'Brain MRI': [
    'Patient Demographics', 'Clinical Indication / History',
    'Procedure Details / Technique / Sequences', 'Comparison Study',
    'Findings (Brain Parenchyma, Ventricles, Extra-axial Spaces, Bones)',
    'Impression / Conclusion', 'Reporting Radiologist Signature',
  ],
  'Abdomen/Pelvis CT': [
    'Patient Demographics', 'Clinical Indication / History',
    'Procedure Details / Contrast Agent Details', 'Comparison Study',
    'Findings (Organ systems detailed description)',
    'Impression / Conclusion', 'Reporting Radiologist Signature',
  ],
  'Pelvis Ultrasound': [
    'Patient Demographics', 'Clinical Indication / History',
    'Procedure Details / Modality Technique',
    'Findings (Uterus, Ovaries, Adnexa, or Bladder / Prostate)',
    'Impression / Conclusion', 'Reporting Radiologist Signature',
  ],
  'Mammography': [
    'Patient Demographics', 'Clinical Indication / History',
    'Procedure Details / Technique',
    'Findings (Breast Density, Calcifications, Masses)',
    'BI-RADS Assessment Category', 'Impression / Recommendations',
    'Reporting Radiologist Signature',
  ],
  'Custom / Other': [],
};

const SAMPLE_REPORTS = {
  'Normal Chest X-Ray (High Quality)': { file: 'sample_reports/chest_xray_normal.txt', modality: 'Chest X-Ray' },
  'Incomplete Brain MRI (Missing Details)': { file: 'sample_reports/brain_mri_incomplete.txt', modality: 'Brain MRI' },
  'Abdomen CT (Logical Contradiction)': { file: 'sample_reports/abdomen_ct_anomaly.txt', modality: 'Abdomen/Pelvis CT' },
};

// ── Navigation ─────────────────────────────────────────────────────────────
function navigate(pageId) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const page = document.getElementById('page-' + pageId);
  if (page) page.classList.add('active');
  const navBtn = document.querySelector(`[data-page="${pageId}"]`);
  if (navBtn) navBtn.classList.add('active');
  document.querySelector('.main-content').scrollTo(0, 0);

  // Page-specific setup
  if (pageId === 'quality') renderQualityDashboard();
  if (pageId === 'suggestions') renderSuggestions();
  if (pageId === 'report') renderReportPage();
  if (pageId === 'dashboard') updateStats();
}

// ── Toast Notifications ────────────────────────────────────────────────────
function toast(msg, type = 'info', duration = 3500) {
  const container = document.getElementById('toast-container');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  container.appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; el.style.transform = 'translateX(20px)'; el.style.transition = '.3s'; setTimeout(() => el.remove(), 300); }, duration);
}

// ── API Key ────────────────────────────────────────────────────────────────
function syncApiKey() {
  const sidebar = document.getElementById('api-key-sidebar');
  const settings = document.getElementById('api-key-settings');
  if (sidebar) App.apiKey = sidebar.value.trim();
  if (settings) settings.value = App.apiKey;
  updateApiStatus();
}

function updateApiStatus() {
  const statusEl = document.getElementById('api-status');
  if (!statusEl) return;
  if (App.apiKey) { statusEl.textContent = '✓ Key entered'; statusEl.className = 'api-status ok'; }
  else { statusEl.textContent = 'No key set'; statusEl.className = 'api-status'; }
}

async function testApiKey() {
  const key = App.apiKey || document.getElementById('api-key-settings')?.value?.trim() || '';
  if (!key) { toast('Enter an API key first.', 'warning'); return; }

  const btn = document.getElementById('test-key-btn');
  const result = document.getElementById('test-result');
  btn.disabled = true; btn.textContent = 'Testing...';

  try {
    // Try backend endpoint first
    const res = await fetch('/api/test-key', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: key, provider: App.provider }),
    });

    if (res.ok) {
      const data = await res.json();
      App.apiKey = key;
      document.getElementById('api-key-sidebar').value = key;
      result.innerHTML = `<span style="color:#065f46;font-weight:600;">${data.message}</span>`;
      updateApiStatus(); toast('API key verified!', 'success');
    } else throw new Error('Backend unverified, trying direct API call...');
  } catch (e) {
    // Fallback to direct client-side test (for GitHub Pages static hosting)
    try {
      if (App.provider === 'groq') {
        const testRes = await fetch('https://api.groq.com/openai/v1/chat/completions', {
          method: 'POST',
          headers: { 'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json' },
          body: JSON.stringify({ model: 'llama-3.3-70b-versatile', messages: [{ role: 'user', content: 'OK' }], max_tokens: 5 })
        });
        if (!testRes.ok) { const err = await testRes.json(); throw new Error(err.error?.message || 'Invalid Groq Key'); }
        result.innerHTML = `<span style="color:#065f46;font-weight:600;">Groq API key verified! (Llama 3.3 70B ready)</span>`;
      } else {
        const testRes = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${key}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ contents: [{ parts: [{ text: 'OK' }] }] })
        });
        if (!testRes.ok) { const err = await testRes.json(); throw new Error(err.error?.message || 'Invalid Gemini Key'); }
        result.innerHTML = `<span style="color:#065f46;font-weight:600;">Gemini API key verified!</span>`;
      }
      App.apiKey = key;
      document.getElementById('api-key-sidebar').value = key;
      updateApiStatus(); toast('API key verified!', 'success');
    } catch (directErr) {
      result.innerHTML = `<span style="color:#991b1b;">${directErr.message}</span>`;
      toast(directErr.message, 'error');
    }
  }
  btn.disabled = false; btn.textContent = '🔌 Test Connection';
}

// ── Stats ──────────────────────────────────────────────────────────────────
function updateStats() {
  const score = App.auditResult?.quality_score ?? '—';
  setText('stat-analyzed', App.reportsAnalyzed);
  setText('stat-score', score);
  setText('stat-api', App.apiKey ? '✓ Connected' : 'Not Set');
  setText('stat-exported', App.reportsExported);
  const apiEl = document.getElementById('stat-api');
  if (apiEl) apiEl.style.color = App.apiKey ? '#10b981' : '#ef4444';
}
function setText(id, val) { const el = document.getElementById(id); if (el) el.textContent = val; }

// ── Upload Page ────────────────────────────────────────────────────────────
function setupUploadPage() {
  const zone = document.getElementById('upload-zone');
  const input = document.getElementById('file-input');
  const select = document.getElementById('modality-select');

  // Drag & drop
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => { e.preventDefault(); zone.classList.remove('drag-over'); if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]); });
  zone.addEventListener('click', () => input.click());
  input.addEventListener('change', () => { if (input.files[0]) handleFile(input.files[0]); });

  // Modality change
  select.addEventListener('change', () => {
    App.modality = select.value;
    renderSectionChips();
  });

  // Text area sync
  document.getElementById('report-textarea').addEventListener('input', function () {
    App.reportText = this.value;
    updateCharCount();
  });

  // Populate modality dropdown
  select.innerHTML = Object.keys(MODALITY_SECTIONS).map(m =>
    `<option value="${m}">${m}</option>`
  ).join('');
  select.value = App.modality;
  renderSectionChips();
}

async function handleFile(file) {
  const allowed = ['.pdf', '.docx', '.txt'];
  const ext = '.' + file.name.split('.').pop().toLowerCase();
  if (!allowed.includes(ext)) { toast('Unsupported file type. Use PDF, DOCX, or TXT.', 'error'); return; }

  toast(`Reading ${file.name}...`);

  // Client-side text reading for TXT files
  if (ext === '.txt') {
    const reader = new FileReader();
    reader.onload = e => {
      App.reportText = e.target.result;
      App.reportFilename = file.name;
      document.getElementById('report-textarea').value = App.reportText;
      document.getElementById('file-badge').textContent = `📄 ${file.name}`;
      document.getElementById('file-badge').style.display = 'inline-flex';
      updateCharCount();
      toast(`✅ Loaded ${App.reportText.length.toLocaleString()} characters`, 'success');
    };
    reader.readAsText(file);
    return;
  }

  // Backend upload if server is available
  const fd = new FormData();
  fd.append('file', file);

  try {
    const res = await fetch('/api/upload', { method: 'POST', body: fd });
    const data = await res.json();
    if (data.error) { toast(data.error, 'error'); return; }

    App.reportText = data.text;
    App.reportFilename = data.filename;
    document.getElementById('report-textarea').value = data.text;
    document.getElementById('file-badge').textContent = `📄 ${data.filename}`;
    document.getElementById('file-badge').style.display = 'inline-flex';
    updateCharCount();
    toast(`✅ Extracted ${data.chars.toLocaleString()} characters from ${data.filename}`, 'success');
  } catch (e) {
    toast('For PDF/DOCX, please paste the text directly into the text area.', 'warning', 5000);
  }
}

async function loadSampleReport(name) {
  const sample = SAMPLE_REPORTS[name];
  if (!sample) return;
  try {
    const res = await fetch(sample.file);
    const text = await res.text();
    App.reportText = text;
    App.reportFilename = sample.file.split('/').pop();
    App.modality = sample.modality;
    document.getElementById('report-textarea').value = text;
    document.getElementById('modality-select').value = sample.modality;
    document.getElementById('file-badge').textContent = `📄 ${App.reportFilename} (sample)`;
    document.getElementById('file-badge').style.display = 'inline-flex';
    updateCharCount();
    renderSectionChips();
    toast(`Loaded sample: ${name}`, 'success');
  } catch (e) {
    toast('Could not load sample: ' + e.message, 'error');
  }
}

function updateCharCount() {
  const el = document.getElementById('char-count');
  if (el) el.textContent = `${App.reportText.length.toLocaleString()} characters`;
}

function clearReport() {
  App.reportText = ''; App.reportFilename = ''; App.auditResult = null;
  document.getElementById('report-textarea').value = '';
  document.getElementById('file-badge').style.display = 'none';
  updateCharCount();
  toast('Report cleared.');
}

function renderSectionChips() {
  App.modality = document.getElementById('modality-select')?.value || App.modality;
  const sections = MODALITY_SECTIONS[App.modality] || [];
  App.mandatorySections = [...sections];

  const container = document.getElementById('section-chips');
  if (!container) return;

  if (App.modality === 'Custom / Other') {
    container.innerHTML = `<textarea class="form-control mt-1" id="custom-sections" rows="4"
      placeholder="One section per line...">${sections.join('\n')}</textarea>`;
    document.getElementById('custom-sections').addEventListener('input', function () {
      App.mandatorySections = this.value.split('\n').map(s => s.trim()).filter(Boolean);
    });
    return;
  }

  container.innerHTML = sections.map(s => `
    <label class="section-chip active" data-section="${s}">
      <input type="checkbox" checked hidden> ${s}
    </label>`).join('');

  container.querySelectorAll('.section-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      chip.classList.toggle('active');
      const sec = chip.dataset.section;
      if (chip.classList.contains('active')) {
        if (!App.mandatorySections.includes(sec)) App.mandatorySections.push(sec);
      } else {
        App.mandatorySections = App.mandatorySections.filter(s => s !== sec);
      }
    });
  });
}

// ── AI Analysis ────────────────────────────────────────────────────────────
async function runAnalysis() {
  App.reportText = document.getElementById('report-textarea')?.value?.trim() || App.reportText;
  const apiKey = App.apiKey || document.getElementById('api-key-sidebar')?.value?.trim() || '';

  if (!App.reportText) { toast('Please upload or paste a report first.', 'error'); return; }
  if (!apiKey) { toast('Please enter your API key in the sidebar.', 'error'); return; }

  App.apiKey = apiKey;
  navigate('analysis');

  const steps = [
    'Sending report to AI...',
    'Evaluating completeness and structure...',
    'Checking medical terminology...',
    'Assessing clinical alignment...',
    'Computing quality score...',
    'Finalizing audit results...',
  ];

  const stepsContainer = document.getElementById('analysis-steps');
  stepsContainer.innerHTML = steps.map((s, i) =>
    `<div class="analysis-step" id="step-${i}"><div class="step-dot"></div>${s}</div>`
  ).join('');

  let stepIdx = 0;
  const stepTimer = setInterval(() => {
    if (stepIdx > 0) document.getElementById(`step-${stepIdx - 1}`)?.classList.replace('active', 'done');
    if (stepIdx < steps.length) {
      document.getElementById(`step-${stepIdx}`)?.classList.add('active');
      stepIdx++;
    }
  }, 800);

  let auditData = null;
  try {
    // Try Flask backend endpoint first
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        api_key: App.apiKey,
        provider: App.provider,
        report_text: App.reportText,
        modality: App.modality,
        mandatory_sections: App.mandatorySections,
      }),
    });

    if (res.ok) {
      auditData = await res.json();
    } else throw new Error('Backend unavailable, switching to browser-direct AI call...');
  } catch (e) {
    // Fallback: Direct API call from browser for static GitHub Pages hosting
    try {
      if (App.provider === 'groq') {
        auditData = await callGroqDirect(App.apiKey, App.reportText, App.modality, App.mandatorySections);
      } else {
        auditData = await callGeminiDirect(App.apiKey, App.reportText, App.modality, App.mandatorySections);
      }
    } catch (directErr) {
      clearInterval(stepTimer);
      showAnalysisError(directErr.message);
      return;
    }
  }

  clearInterval(stepTimer);
  steps.forEach((_, i) => {
    const el = document.getElementById(`step-${i}`);
    if (el) { el.classList.remove('active'); el.classList.add('done'); }
  });

  if (auditData.error) {
    showAnalysisError(auditData.error);
  } else {
    App.auditResult = auditData;
    App.auditTimestamp = new Date().toISOString();
    App.reportsAnalyzed++;
    updateStats();
    setTimeout(() => { navigate('quality'); toast('✅ Analysis complete!', 'success'); }, 600);
  }
}

const SYSTEM_INSTRUCTIONS_PROMPT = "You are a board-certified Quality Assurance Radiologist and Clinical Audit Specialist with 20+ years of experience. Your sole task is to AUDIT and EVALUATE radiology reports for quality, completeness, and clinical accuracy. CRITICAL DIRECTIVE: Do NOT generate a new radiology report. Do NOT write diagnoses. Do NOT add findings. Your role is purely evaluative — assess the existing report and provide structured quality feedback.";

function buildAuditPrompt(reportText, modality, mandatorySections) {
  const secStr = mandatorySections.map(s => `  - ${s}`).join('\n') || '  - (none specified)';
  return `Audit the following radiology report with professional clinical QA standards.

EXAMINATION TYPE / MODALITY: ${modality}

MANDATORY SECTIONS TO VERIFY:
${secStr}

REPORT CONTENT:
"""
${reportText}
"""

AUDIT TASKS:
1. Quality Score: Rate 0-100.
2. Readiness Status: "ready_for_approval", "minor_revision_required", or "major_revision_required".
3. Quality Breakdown: 0-100 for completeness, terminology, clinical_alignment, formatting, impression_quality.
4. Strengths: 2-4 strengths.
5. Missing Sections: list mandatory sections absent.
6. Section Audit: present (true/false) & details for each section.
7. AI Suggestions (missing_sections, template_compliance, medical_terminology, formatting_improvements, impression_suggestions, overall_remarks).
8. Overall Remarks: 2-3 sentence summary.

Return ONLY a valid JSON object matching this EXACT schema (no markdown fences, no extra text):
{
  "quality_score": 85,
  "score_justification": "string",
  "readiness_status": "ready_for_approval",
  "quality_breakdown": {
    "completeness": 90, "terminology": 85, "clinical_alignment": 85, "formatting": 80, "impression_quality": 85
  },
  "strengths": ["string"],
  "missing_sections_list": ["string"],
  "mandatory_sections": [{"name": "string", "present": true, "details": "string"}],
  "ai_suggestions": {
    "missing_sections": ["string"], "template_compliance": ["string"], "medical_terminology": ["string"],
    "formatting_improvements": ["string"], "impression_suggestions": ["string"], "overall_remarks": ["string"]
  },
  "overall_remarks": "string"
}`;
}

async function callGroqDirect(apiKey, reportText, modality, mandatorySections) {
  const prompt = buildAuditPrompt(reportText, modality, mandatorySections);
  const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + apiKey, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'llama-3.3-70b-versatile',
      messages: [{ role: 'system', content: SYSTEM_INSTRUCTIONS_PROMPT }, { role: 'user', content: prompt }],
      temperature: 0.2,
      response_format: { type: 'json_object' }
    })
  });
  if (!res.ok) { const err = await res.json(); throw new Error(err.error?.message || 'Groq API request failed'); }
  const data = await res.json();
  return JSON.parse(data.choices[0].message.content);
}

async function callGeminiDirect(apiKey, reportText, modality, mandatorySections) {
  const prompt = buildAuditPrompt(reportText, modality, mandatorySections);
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: { responseMimeType: 'application/json', temperature: 0.2 }
    })
  });
  if (!res.ok) { const err = await res.json(); throw new Error(err.error?.message || 'Gemini API request failed'); }
  const data = await res.json();
  return JSON.parse(data.candidates[0].content.parts[0].text);
}

function showAnalysisError(msg) {
  const el = document.getElementById('analysis-error');
  if (el) { el.style.display = 'block'; el.querySelector('.error-msg').textContent = msg; }
  document.getElementById('analysis-spinner-wrap').style.display = 'none';
  toast(msg, 'error', 6000);
}

// ── Quality Dashboard ──────────────────────────────────────────────────────
function renderQualityDashboard() {
  const res = App.auditResult;
  if (!res) return;

  const score = res.quality_score || 0;
  const status = res.readiness_status || '';
  const bd = res.quality_breakdown || {};

  // Score Gauge
  drawGauge(score);
  setText('gauge-score-text', score);
  const justEl = document.getElementById('gauge-justification');
  if (justEl) justEl.textContent = res.score_justification || '';

  // Readiness badge
  const badgeEl = document.getElementById('readiness-badge');
  if (badgeEl) {
    const map = {
      ready_for_approval: { cls: 'readiness-ready', label: '✅ Ready for Approval' },
      minor_revision_required: { cls: 'readiness-minor', label: '⚠️ Minor Revision Required' },
      major_revision_required: { cls: 'readiness-major', label: '🔴 Major Revision Required' },
    };
    const info = map[status] || { cls: 'readiness-minor', label: status };
    badgeEl.className = `readiness-badge ${info.cls}`;
    badgeEl.textContent = info.label;
  }

  // Strengths
  const strengthEl = document.getElementById('strengths-list');
  if (strengthEl) {
    const strengths = res.strengths || [];
    strengthEl.innerHTML = strengths.length
      ? strengths.map(s => `<div class="strength-item"><span>⭐</span><span>${s}</span></div>`).join('')
      : '<p class="text-muted text-small">No specific strengths listed.</p>';
  }

  // Summary
  setText('exec-summary', res.overall_remarks || 'No summary available.');

  // Missing sections
  const missingEl = document.getElementById('missing-sections');
  if (missingEl) {
    const missing = res.missing_sections_list || [];
    missingEl.innerHTML = missing.length
      ? missing.map(m => `<div style="background:#fee2e2;border:1px solid #fecaca;border-radius:8px;padding:.3rem .8rem;margin-bottom:.35rem;font-size:.82rem;font-weight:600;color:#991b1b;">✗ ${m}</div>`).join('')
      : '<div style="color:#065f46;font-weight:600;font-size:.88rem;">✅ All sections present</div>';
  }

  // Quality breakdown bars
  renderBreakdown(bd);

  // Section checklist
  renderChecklist(res.mandatory_sections || []);
}

function drawGauge(score) {
  const radius = 80;
  const circ = 2 * Math.PI * radius;
  const offset = circ * (1 - score / 100);

  const scoreColor = score >= 85 ? '#10b981' : score >= 65 ? '#f59e0b' : '#ef4444';
  const label = score >= 85 ? 'Excellent Quality' : score >= 65 ? 'Needs Minor Review' : 'Major Revision Required';

  const gaugeEl = document.getElementById('score-gauge-svg');
  if (!gaugeEl) return;

  gaugeEl.innerHTML = `
    <circle cx="100" cy="100" r="${radius}" fill="none" stroke="#e2e8f0" stroke-width="13"/>
    <circle cx="100" cy="100" r="${radius}" fill="none"
      stroke="${scoreColor}" stroke-width="13" stroke-linecap="round"
      stroke-dasharray="${circ.toFixed(1)}" stroke-dashoffset="${circ.toFixed(1)}"
      transform="rotate(-90 100 100)"
      id="gauge-arc"
      style="transition: stroke-dashoffset 1.4s cubic-bezier(.4,0,.2,1); filter: drop-shadow(0 0 6px ${scoreColor}44)"/>
    <text x="100" y="94" text-anchor="middle" font-family="Inter,sans-serif" font-weight="800" font-size="34" fill="${scoreColor}">${score}</text>
    <text x="100" y="115" text-anchor="middle" font-family="Inter,sans-serif" font-weight="500" font-size="11" fill="#94a3b8">out of 100</text>
  `;

  const labelEl = document.getElementById('gauge-label');
  if (labelEl) { labelEl.textContent = label; labelEl.style.color = scoreColor; }

  requestAnimationFrame(() => {
    setTimeout(() => {
      const arc = document.getElementById('gauge-arc');
      if (arc) arc.style.strokeDashoffset = offset.toFixed(1);
    }, 80);
  });
}

function renderBreakdown(bd) {
  const dims = [
    { key: 'completeness', label: '📋 Completeness', color: '#0d9488' },
    { key: 'terminology', label: '🔬 Medical Terminology', color: '#8b5cf6' },
    { key: 'clinical_alignment', label: '⚖️ Clinical Alignment', color: '#f59e0b' },
    { key: 'formatting', label: '📐 Formatting', color: '#3b82f6' },
    { key: 'impression_quality', label: '🎯 Impression Quality', color: '#10b981' },
  ];
  const el = document.getElementById('breakdown-bars');
  if (!el) return;
  el.innerHTML = dims.map(d => {
    const val = bd[d.key] || 0;
    return `<div class="breakdown-row">
      <div class="breakdown-label-row">
        <span>${d.label}</span>
        <span class="breakdown-val" style="color:${d.color}">${val}/100</span>
      </div>
      <div class="breakdown-track">
        <div class="breakdown-fill" style="width:0%;background:${d.color}" data-target="${val}"></div>
      </div>
    </div>`;
  }).join('');

  setTimeout(() => {
    el.querySelectorAll('.breakdown-fill').forEach(bar => {
      bar.style.width = bar.dataset.target + '%';
    });
  }, 100);
}

function renderChecklist(sections) {
  const el = document.getElementById('section-checklist');
  if (!el || !sections.length) return;
  const presentCount = sections.filter(s => s.present).length;
  const pct = Math.round(presentCount / sections.length * 100);
  const pctColor = pct >= 85 ? '#10b981' : pct >= 60 ? '#f59e0b' : '#ef4444';

  const header = document.getElementById('checklist-header');
  if (header) {
    header.innerHTML = `
      <span style="font-size:.88rem;font-weight:600;color:#64748b;">${presentCount}/${sections.length} sections present</span>
      <span class="checklist-pct" style="color:${pctColor}">${pct}%</span>`;
  }

  el.innerHTML = sections.map(s => `
    <div class="checklist-item">
      <div class="check-dot ${s.present ? 'dot-ok' : 'dot-bad'}">${s.present ? '✓' : '✗'}</div>
      <div>
        <div class="check-name">${s.name}</div>
        ${s.details ? `<div class="check-detail">${s.details}</div>` : ''}
      </div>
    </div>`).join('');
}

// ── AI Suggestions ─────────────────────────────────────────────────────────
function renderSuggestions() {
  const res = App.auditResult;
  if (!res) return;
  const sugs = res.ai_suggestions || {};

  const total = Object.values(sugs).reduce((a, v) => a + (Array.isArray(v) ? v.length : 0), 0);
  setText('sug-total', total);
  setText('sug-missing', (sugs.missing_sections || []).length);
  setText('sug-score', res.quality_score || 0);

  const map = {
    'tab-missing': { key: 'missing_sections', cls: 'sug-missing', icon: '🔴', label: 'Missing Sections' },
    'tab-template': { key: 'template_compliance', cls: 'sug-template', icon: '🔵', label: 'Template Compliance' },
    'tab-terminology': { key: 'medical_terminology', cls: 'sug-terminology', icon: '🟣', label: 'Medical Terminology' },
    'tab-formatting': { key: 'formatting_improvements', cls: 'sug-formatting', icon: '🟢', label: 'Formatting' },
    'tab-impression': { key: 'impression_suggestions', cls: 'sug-impression', icon: '🟠', label: 'Impression' },
    'tab-remarks': { key: 'overall_remarks', cls: 'sug-remarks', icon: '⚫', label: 'Remarks' },
  };

  Object.entries(map).forEach(([tabId, cfg]) => {
    const el = document.getElementById(tabId);
    const items = sugs[cfg.key] || [];
    if (!el) return;
    if (!items.length) {
      el.innerHTML = `<div style="color:#065f46;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:1rem;font-weight:600;">✅ No issues in this category.</div>`;
    } else {
      el.innerHTML = items.map(item => `
        <div class="sug-card ${cfg.cls}">
          <div class="sug-title">${cfg.icon} ${cfg.label}</div>
          <div class="sug-text">${item}</div>
        </div>`).join('');
    }
  });
}

function switchTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelector(`[data-tab="${tabId}"]`)?.classList.add('active');
  document.getElementById(tabId)?.classList.add('active');
}

// ── Audit Report Page ──────────────────────────────────────────────────────
function renderReportPage() {
  const res = App.auditResult;
  if (!res) return;

  const score = res.quality_score || 0;
  const status = res.readiness_status || '';
  const map = {
    ready_for_approval: { label: '✅ Ready for Approval', color: '#065f46', bg: '#d1fae5' },
    minor_revision_required: { label: '⚠️ Minor Revision Required', color: '#92400e', bg: '#fef3c7' },
    major_revision_required: { label: '🔴 Major Revision Required', color: '#991b1b', bg: '#fee2e2' },
  };
  const info = map[status] || { label: 'Unknown', color: '#334155', bg: '#f1f5f9' };
  const scoreColor = score >= 85 ? '#10b981' : score >= 65 ? '#f59e0b' : '#ef4444';
  const ts = App.auditTimestamp ? new Date(App.auditTimestamp).toLocaleString() : 'N/A';
  const totalSugs = Object.values(res.ai_suggestions || {}).reduce((a, v) => a + (Array.isArray(v) ? v.length : 0), 0);
  const missing = res.missing_sections_list || [];

  const el = document.getElementById('report-preview-content');
  if (el) {
    el.innerHTML = `
      <div class="rp-header">
        <div class="rp-app-name">⚕️ AI-Powered Radiology Report Audit</div>
        <div class="rp-type">Quality Assurance Report</div>
      </div>
      <div class="rp-meta-row"><span class="rp-meta-key">📄 Report</span><span class="rp-meta-val">${App.reportFilename || 'Pasted Report'}</span></div>
      <div class="rp-meta-row"><span class="rp-meta-key">🩺 Modality</span><span class="rp-meta-val">${App.modality}</span></div>
      <div class="rp-meta-row"><span class="rp-meta-key">📅 Audit Date</span><span class="rp-meta-val">${ts}</span></div>
      <div class="rp-score-block">
        <div class="rp-score-num" style="color:${scoreColor}">${score}</div>
        <div>
          <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;font-weight:600">Quality Score</div>
          <div style="display:inline-block;padding:.2rem .65rem;border-radius:50px;font-size:.8rem;font-weight:700;background:${info.bg};color:${info.color};margin-top:.25rem">${info.label}</div>
        </div>
      </div>
      <div style="margin-top:.85rem;font-size:.83rem;color:#64748b;">
        ${missing.length ? `<b>Missing:</b> ${missing.join(', ')}<br>` : '✅ <b>All sections present</b><br>'}
        <b>Strengths:</b> ${(res.strengths || []).length} &nbsp;|&nbsp; <b>Suggestions:</b> ${totalSugs}
      </div>`;
  }
}

async function downloadPDF() {
  if (!App.auditResult) { toast('No audit results. Run analysis first.', 'error'); return; }

  const btn = document.getElementById('pdf-download-btn');
  btn.disabled = true; btn.textContent = '⏳ Generating PDF...';

  try {
    const res = await fetch('/api/generate-pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename: App.reportFilename || 'report.txt',
        modality: App.modality,
        audit_result: App.auditResult,
      }),
    });

    if (!res.ok) {
      // Print window fallback if server is not available
      window.print();
    } else {
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `radiology_audit_${(App.reportFilename || 'report').replace(/\.[^.]+$/, '')}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      App.reportsExported++;
      updateStats();
      toast('✅ PDF downloaded!', 'success');
    }
  } catch (e) {
    window.print();
  }
  btn.disabled = false; btn.textContent = '⬇️ Download PDF Audit Report';
}

function downloadJSON() {
  if (!App.auditResult) { toast('No audit results.', 'error'); return; }
  const blob = new Blob([JSON.stringify(App.auditResult, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `radiology_audit_${(App.reportFilename || 'report').replace(/\.[^.]+$/, '')}.json`;
  a.click();
  URL.revokeObjectURL(url);
  toast('JSON exported!', 'success');
}

// ── Init ───────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Nav items
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => navigate(btn.dataset.page));
  });

  // API key sidebar
  const sidebarKey = document.getElementById('api-key-sidebar');
  if (sidebarKey) {
    sidebarKey.addEventListener('input', syncApiKey);
    sidebarKey.addEventListener('change', syncApiKey);
  }

  // Setup upload page interactions
  setupUploadPage();

  // Sample report picker
  const samplePicker = document.getElementById('sample-picker');
  if (samplePicker) {
    samplePicker.addEventListener('change', () => {
      if (samplePicker.value) loadSampleReport(samplePicker.value);
    });
  }

  // Analyze button
  document.getElementById('analyze-btn')?.addEventListener('click', runAnalysis);

  // Retry analysis
  document.getElementById('retry-btn')?.addEventListener('click', () => { navigate('upload'); });

  // PDF download
  document.getElementById('pdf-download-btn')?.addEventListener('click', downloadPDF);

  // JSON download
  document.getElementById('json-download-btn')?.addEventListener('click', downloadJSON);

  // Test key button
  document.getElementById('test-key-btn')?.addEventListener('click', testApiKey);

  // Provider selector listener
  const providerSelect = document.getElementById('provider-select');
  if (providerSelect) {
    providerSelect.addEventListener('change', () => {
      App.provider = providerSelect.value;
      const isGroq = App.provider === 'groq';
      const labelText = isGroq ? '🔑 Groq API Key' : '🔑 Gemini API Key';
      const placeholder = isGroq ? 'gsk_...' : 'AIzaSy...';

      document.getElementById('sidebar-provider-label').textContent = labelText;
      document.getElementById('api-key-label').textContent = labelText;
      document.getElementById('api-key-sidebar').placeholder = placeholder;
      document.getElementById('api-key-settings').placeholder = placeholder;
    });
  }

  // Settings page key input
  const settingsKey = document.getElementById('api-key-settings');
  if (settingsKey) {
    settingsKey.addEventListener('input', () => {
      App.apiKey = settingsKey.value.trim();
      document.getElementById('api-key-sidebar').value = App.apiKey;
      updateApiStatus();
    });
  }

  // Navigate to quality / suggestions nav buttons
  document.getElementById('goto-quality-btn')?.addEventListener('click', () => navigate('quality'));
  document.getElementById('goto-suggestions-btn')?.addEventListener('click', () => navigate('suggestions'));
  document.getElementById('goto-report-btn')?.addEventListener('click', () => navigate('report'));
  document.getElementById('goto-upload-btn')?.addEventListener('click', () => navigate('upload'));

  // Pre-fill default key if configured
  if (DEFAULT_API_KEY) {
    document.getElementById('api-key-sidebar').value = DEFAULT_API_KEY;
    const settingsInput = document.getElementById('api-key-settings');
    if (settingsInput) settingsInput.value = DEFAULT_API_KEY;
    updateApiStatus();
  }

  // Initial state
  navigate('dashboard');
  updateStats();
});
