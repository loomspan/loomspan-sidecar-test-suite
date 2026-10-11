"""Decode complete inline or chunked trace evidence, independent of suite semantics."""
import json


def payload(record, records):
    if record.get('data') is not None:
        return record['data']
    meta = record['metadata']
    chunks = sorted((r for r in records if r['recordType'] == 'PAYLOAD_CHUNK_APPENDED'
                     and r['metadata'].get('payloadId') == meta.get('payloadId')),
                    key=lambda r: r['metadata']['chunkIndex'])
    if len(chunks) != meta.get('chunkCount') or [c['metadata']['chunkIndex'] for c in chunks] != list(range(len(chunks))):
        raise ValueError('Incomplete or duplicate trace payload chunks')
    return json.loads(''.join(c['data'] for c in chunks))
