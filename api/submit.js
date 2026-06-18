/**
 * api/submit.js  —  Vercel Serverless Function
 *
 * Receives a JSON POST from the apply / restructuring-apply forms,
 * formats a styled HTML email, and delivers it via Resend's API.
 *
 * Environment variables (Vercel → Settings → Environment Variables):
 *   RESEND_API_KEY   your Resend API key (starts with "re_")
 *   TO_EMAIL         where submissions land, e.g. qumsieh.luca@gmail.com
 *   FROM_EMAIL       your verified sender, e.g. intake@archangel-finance.com
 */

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { RESEND_API_KEY, TO_EMAIL, FROM_EMAIL } = process.env;
  if (!RESEND_API_KEY || !TO_EMAIL || !FROM_EMAIL) {
    console.error('Missing env vars:', { RESEND_API_KEY: !!RESEND_API_KEY, TO_EMAIL: !!TO_EMAIL, FROM_EMAIL: !!FROM_EMAIL });
    return res.status(500).json({ error: 'Server not configured — contact the administrator.' });
  }

  const data = req.body;
  if (!data || typeof data !== 'object') {
    return res.status(400).json({ error: 'Invalid request body.' });
  }

  const isRestructuring = data.formType === 'restructuring';
  const formLabel = isRestructuring ? 'Debt Restructuring Review' : 'Funding Application';
  const bizName   = data.businessName || 'Unknown Business';

  // reply_to the applicant so hitting Reply in Zoho/Gmail goes straight to them
  const replyTo = data.own1Email
    ? (data.own1Name ? `${data.own1Name} <${data.own1Email}>` : data.own1Email)
    : undefined;

  try {
    const resendRes = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${RESEND_API_KEY}`,
      },
      body: JSON.stringify({
        from:     `Archangel Finance <${FROM_EMAIL}>`,
        to:       [TO_EMAIL],
        reply_to: replyTo,
        subject:  `New ${formLabel} — ${bizName}`,
        html:     buildHtml(data, isRestructuring),
      }),
    });

    if (!resendRes.ok) {
      const detail = await resendRes.text();
      console.error('Resend error:', resendRes.status, detail);
      return res.status(502).json({ error: 'Email delivery failed. Try again.' });
    }

    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error('Unexpected error in /api/submit:', err);
    return res.status(500).json({ error: 'Server error. Try again.' });
  }
}

/* ─── Email HTML builder ──────────────────────────────────────────────────── */

function row(label, value) {
  if (!value) return '';
  return `<tr>
    <td style="padding:7px 14px;color:#888;font-size:12px;white-space:nowrap;vertical-align:top;width:38%">${esc(label)}</td>
    <td style="padding:7px 14px;color:#111;font-size:13px;font-weight:600;vertical-align:top">${esc(value)}</td>
  </tr>`;
}

function section(title, rows) {
  const body = rows.filter(Boolean).join('');
  if (!body) return '';
  return `
  <div style="margin-bottom:22px">
    <div style="background:#1a1612;color:#c9a84c;font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:7px 14px">${esc(title)}</div>
    <table style="width:100%;border-collapse:collapse;background:#fff;border:1px solid #e2dbd0;border-top:none">${body}</table>
  </div>`;
}

function ownerSection(data, idx) {
  const name = data[`own${idx}Name`];
  if (!name) return '';
  const ordinals = ['First', 'Second', 'Third', 'Fourth'];
  const ssn = data[`own${idx}Ssn`];
  const maskedSsn = ssn ? '•••–••–' + ssn.replace(/\D/g, '').slice(-4) : '';
  return section(`${ordinals[idx - 1]} Owner`, [
    row('Name',         name),
    row('Ownership %',  data[`own${idx}Pct`]   ? data[`own${idx}Pct`] + '%' : ''),
    row('Date of Birth',data[`own${idx}Dob`]),
    row('SSN (last 4)', maskedSsn),
    row('Phone',        data[`own${idx}Phone`]),
    row('Home Address', data[`own${idx}Address`]),
    row('Email',        data[`own${idx}Email`]),
  ]);
}

function buildHtml(data, isRestructuring) {
  const now = new Date().toLocaleString('en-US', {
    timeZone: 'America/New_York',
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
    hour: 'numeric', minute: '2-digit',
  });

  // Debt obligation table (restructuring form)
  let debtHtml = '';
  if (Array.isArray(data.debtRows) && data.debtRows.length) {
    const thead = ['Funder', 'Original Amt', 'Balance', 'Payment', 'Frequency', 'End Date']
      .map(h => `<th style="padding:5px 10px;text-align:left;font-size:11px;border:1px solid #e2dbd0;color:#888;background:#faf8f4">${h}</th>`)
      .join('');
    const tbody = data.debtRows.map(r => {
      const cells = [r.funder, r.originalAmt, r.balance, r.payment, r.frequency, r.endDate]
        .map(v => `<td style="padding:5px 10px;font-size:12px;border:1px solid #e2dbd0">${esc(v || '—')}</td>`)
        .join('');
      return `<tr>${cells}</tr>`;
    }).join('');
    debtHtml = `
    <div style="margin-bottom:22px">
      <div style="background:#1a1612;color:#c9a84c;font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:7px 14px">Current Debt Obligations</div>
      <div style="overflow-x:auto;border:1px solid #e2dbd0;border-top:none;background:#fff">
        <table style="width:100%;border-collapse:collapse;min-width:520px">
          <thead><tr>${thead}</tr></thead>
          <tbody>${tbody}</tbody>
        </table>
      </div>
    </div>`;
  }

  // Active advances table (funding form)
  let advancesHtml = '';
  if (Array.isArray(data.advances) && data.advances.length) {
    const thead = ['Funder', 'Original', 'Balance', 'Frequency', 'Payoff']
      .map(h => `<th style="padding:5px 10px;text-align:left;font-size:11px;border:1px solid #e2dbd0;color:#888;background:#faf8f4">${h}</th>`)
      .join('');
    const tbody = data.advances.map(a => {
      const cells = Object.values(a)
        .map(v => `<td style="padding:5px 10px;font-size:12px;border:1px solid #e2dbd0">${esc(String(v || '—'))}</td>`)
        .join('');
      return `<tr>${cells}</tr>`;
    }).join('');
    advancesHtml = `
    <div style="margin-bottom:22px">
      <div style="background:#1a1612;color:#c9a84c;font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:7px 14px">Active Advances</div>
      <div style="border:1px solid #e2dbd0;border-top:none;background:#fff">
        <table style="width:100%;border-collapse:collapse">
          <thead><tr>${thead}</tr></thead>
          <tbody>${tbody}</tbody>
        </table>
      </div>
    </div>`;
  }

  // Business info differs between the two forms
  const bizRows = isRestructuring
    ? [
        row('Company Name',    data.businessName),
        row('Entity Type',     data.entityType),
        row('Industry',        data.industry),
        row('Tax ID / EIN',    data.ein),
        row('Annual Revenue',  data.annualRevenue),
        row('Time in Business',data.timeInBusiness),
        row('Business Phone',  data.bizPhone),
        row('Business Address',data.bizAddress),
      ]
    : [
        row('Company Name',    data.businessName),
        row('Desired Amount',  data.fundingAmount),
        row('Use of Funds',    data.useOfFunds),
        row('Annual Revenue',  data.annualRevenue),
        row('Time in Business',data.timeInBusiness),
        row('Industry',        data.industry),
        row('Entity Type',     data.entityType),
        row('Tax ID / EIN',    data.ein),
        row('Business Phone',  data.bizPhone),
        row('Business Address',data.bizAddress),
      ];

  const formLabel = isRestructuring ? 'Debt Restructuring Review' : 'Funding Application';

  return `<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:32px 16px;background:#f0ebe3;font-family:Georgia,'Times New Roman',serif">
<div style="max-width:620px;margin:0 auto;background:#faf8f4;border:1px solid #d4cec5;border-radius:3px;overflow:hidden">

  <!-- Header -->
  <div style="background:#0d0c0b;padding:22px 26px;border-bottom:2px solid #9c7c3c">
    <div style="font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:#9c7c3c;margin-bottom:6px">Archangel Finance</div>
    <div style="font-size:20px;color:#f8f5ef;font-weight:400;margin-bottom:4px">New ${esc(formLabel)}</div>
    <div style="font-size:11px;color:#666">${esc(now)}</div>
  </div>

  <!-- Body -->
  <div style="padding:24px 26px">
    ${section(isRestructuring ? 'Business Information' : 'Funding Request', bizRows)}
    ${ownerSection(data, 1)}
    ${ownerSection(data, 2)}
    ${ownerSection(data, 3)}
    ${ownerSection(data, 4)}
    ${debtHtml}
    ${advancesHtml}
    ${section('Signature', [
      row('Signed by', data.sigName),
      row('Date',      data.sigDate),
    ])}
  </div>

  <!-- Footer -->
  <div style="background:#0d0c0b;padding:12px 26px;font-size:11px;color:#555;border-top:1px solid #1e1c19">
    Submitted via archangelfinance.com &mdash; hit <strong style="color:#9c7c3c">Reply</strong> in Gmail to respond from your custom address.
  </div>

</div>
</body>
</html>`;
}

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
