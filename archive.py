"""Unsaid Archive: local semantic passage discovery, never generated testimony."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path

MODEL = 'sentence-transformers/all-MiniLM-L6-v2'


def passages(documents):
    result = []
    seen = set()
    for doc in documents:
        if not isinstance(doc, dict) or not isinstance(doc.get('id'), str) or not doc['id'].strip():
            raise ValueError('Every document needs a nonempty id')
        if doc['id'] in seen:
            raise ValueError('Duplicate document id')
        seen.add(doc['id'])
        text = doc.get('text')
        if not isinstance(text, str) or not text.strip():
            raise ValueError('Every document needs text')
        # Exact character offsets survive punctuation, Unicode and blank lines.
        for match in re.finditer(r'[^\n]+', text):
            if match.group().strip():
                result.append({'document': doc['id'], 'start': match.start(),
                               'end': match.end(), 'quote': match.group(),
                               'source_sha256': hashlib.sha256(text.encode()).hexdigest()})
    if not result or len(result) > 200:
        raise ValueError('Provide 1 to 200 nonempty lines')
    return result


class Archive:
    def __init__(self, documents, cache):
        os.environ['HF_HUB_OFFLINE'] = '1'
        os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN'] = '1'
        import torch
        from transformers import AutoModel, AutoTokenizer
        self.torch = torch
        self.items = passages(documents)
        opts = dict(cache_dir=str(cache), token=False, local_files_only=True,
                    trust_remote_code=False)
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL, **opts)
        self.model = AutoModel.from_pretrained(MODEL, use_safetensors=True, **opts).eval()
        self.revision = getattr(self.model.config, '_commit_hash', None)
        self.vectors = self.encode([p['quote'] for p in self.items])

    def encode(self, texts):
        if any(not isinstance(t, str) or not t.strip() for t in texts):
            raise ValueError('Text must not be blank')
        if any(len(self.tokenizer(t)['input_ids']) > 256 for t in texts):
            raise ValueError('Split long lines or questions: maximum 256 model tokens')
        inputs = self.tokenizer(texts, padding=True, return_tensors='pt')
        with self.torch.inference_mode():
            hidden = self.model(**inputs).last_hidden_state
            mask = inputs['attention_mask'].unsqueeze(-1)
            vectors = (hidden * mask).sum(1) / mask.sum(1).clamp(min=1)
            return self.torch.nn.functional.normalize(vectors, p=2, dim=1)

    def search(self, query, threshold=0.4):
        if not 0 <= threshold <= 1:
            raise ValueError('Threshold must be between zero and one')
        scores = (self.encode([query]) @ self.vectors.T)[0].tolist()
        ranked = sorted(range(len(scores)), key=lambda i: (-scores[i], i))[:3]
        return {'query': query, 'model': MODEL, 'revision': self.revision,
                'threshold': threshold, 'status': 'related_passages' if scores[ranked[0]] >= threshold else 'no_close_match',
                'notice': 'Related wording is not an answer or proof. Nothing is spoken on behalf of the writer. A low score does not prove absence.',
                'matches': [dict(self.items[i], score=scores[i], above_threshold=scores[i] >= threshold) for i in ranked]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive', type=Path)
    p.add_argument('query')
    p.add_argument('--cache', required=True, type=Path)
    p.add_argument('--threshold', type=float, default=0.4)
    args = p.parse_args()
    a = Archive(json.loads(args.archive.read_text()), args.cache)
    print(json.dumps(a.search(args.query, args.threshold), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
