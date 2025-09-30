import { google } from 'googleapis';
import { getGoogleAuth } from './auth.js';

export async function appendProposals(rows: Array<Array<string | number>>) {
  const spreadsheetId = process.env.GOOGLE_SHEETS_ID || '';
  if (!spreadsheetId) throw new Error('Missing GOOGLE_SHEETS_ID');

  const auth = getGoogleAuth();
  const sheets = google.sheets({ version: 'v4', auth });
  const range = 'Proposals!A:Z';
  await sheets.spreadsheets.values.append({
    spreadsheetId,
    range,
    valueInputOption: 'USER_ENTERED',
    requestBody: { values: rows }
  });
}

export async function ensureProposalsHeader() {
  const spreadsheetId = process.env.GOOGLE_SHEETS_ID || '';
  const auth = getGoogleAuth();
  const sheets = google.sheets({ version: 'v4', auth });
  const header = [
    'CallDate','ExtractedCase','ExistingRuleMatched','SuggestedRuleDiff','Confidence','Status','Notes'
  ];
  // Try read first row; if empty, set header
  const res = await sheets.spreadsheets.values.get({ spreadsheetId, range: 'Proposals!A1:G1' }).catch(() => null);
  const values = res?.data.values || [];
  if (!values.length || values[0].every(c => !c)) {
    await sheets.spreadsheets.values.update({
      spreadsheetId,
      range: 'Proposals!A1:G1',
      valueInputOption: 'RAW',
      requestBody: { values: [header] }
    });
  }
}

