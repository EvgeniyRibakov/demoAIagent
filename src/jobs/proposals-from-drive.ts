import 'dotenv/config';
import { listTextFilesInFolder, downloadFileContent } from '../google/drive.js';
import { ensureProposalsHeader, appendProposals } from '../google/sheets.js';
import { extractProposalsFromTranscript } from '../llm/extract.js';

async function main() {
  const folderId = process.env.GOOGLE_DRIVE_CALLS_FOLDER_ID || '';
  if (!folderId) throw new Error('Missing GOOGLE_DRIVE_CALLS_FOLDER_ID');

  await ensureProposalsHeader();

  const files = await listTextFilesInFolder(folderId);
  if (!files.length) {
    console.log('No transcripts found');
    return;
  }

  for (const f of files) {
    const text = await downloadFileContent(f);
    const proposals = await extractProposalsFromTranscript(text);
    if (!proposals.length) continue;
    const rows = proposals.map(p => [
      p.callDate,
      p.extractedCase,
      p.existingRuleMatched,
      p.suggestedRuleDiff,
      p.confidence,
      p.status,
      p.notes
    ]);
    await appendProposals(rows);
    console.log(`Wrote ${rows.length} proposals from ${f.name}`);
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});


