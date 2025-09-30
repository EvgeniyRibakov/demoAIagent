import { google } from 'googleapis';
import { getGoogleAuth } from './auth.js';

export interface DriveFileMeta {
  id: string;
  name: string;
  mimeType: string;
  modifiedTime?: string;
}

export async function listTextFilesInFolder(folderId: string): Promise<DriveFileMeta[]> {
  const auth = getGoogleAuth();
  const drive = google.drive({ version: 'v3', auth });
  const q = `'${folderId}' in parents and trashed = false and (mimeType='text/plain' or mimeType='application/json' or mimeType='application/vnd.google-apps.document')`;
  const res = await drive.files.list({
    q,
    fields: 'files(id,name,mimeType,modifiedTime)'
  });
  return (res.data.files || []).map(f => ({
    id: f.id!,
    name: f.name || '',
    mimeType: f.mimeType || 'text/plain',
    modifiedTime: f.modifiedTime || undefined
  }));
}

export async function downloadFileContent(file: DriveFileMeta): Promise<string> {
  const auth = getGoogleAuth();
  const drive = google.drive({ version: 'v3', auth });
  // For Google Docs, export as TXT
  if (file.mimeType === 'application/vnd.google-apps.document') {
    const res = await drive.files.export({ fileId: file.id, mimeType: 'text/plain' }, { responseType: 'text' });
    return String(res.data || '');
  }
  const res = await drive.files.get({ fileId: file.id, alt: 'media' }, { responseType: 'text' });
  return String(res.data || '');
}

