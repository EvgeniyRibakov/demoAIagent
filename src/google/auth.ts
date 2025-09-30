import { google } from 'googleapis';

export function getGoogleAuth() {
  const clientEmail = process.env.GOOGLE_CLIENT_EMAIL || '';
  const privateKey = (process.env.GOOGLE_PRIVATE_KEY || '').replace(/\\n/g, '\n');
  if (!clientEmail || !privateKey) {
    throw new Error('Missing GOOGLE_CLIENT_EMAIL or GOOGLE_PRIVATE_KEY');
  }

  const scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.readonly'
  ];

  return new google.auth.JWT({
    email: clientEmail,
    key: privateKey,
    scopes
  });
}

