# Unsaid Archive

A local semantic reading room for the gaps in a written memory. This new prototype was begun on 28 October 2026 KST for DEV Hacktoberfest Week 4. It retrieves exact source passages; it never generates testimony or impersonates the writer.

## Current state

Working Python retrieval core, local browser reading room and fictional demonstration letters. The public browser demo is available at https://estona815.github.io/unsaid-archive/ . The contest entry is being finalized. OpenAI Codex authored the code, fictional text and documentation under the entrant's direction. Existing open model weights/runtime are reused; BatchDay's task-batching application is not reused.

## Run

Python with PyTorch and Hugging Face Transformers is required. Supply an existing local cache for `sentence-transformers/all-MiniLM-L6-v2` (Apache-2.0). There are no inference credentials, paid API calls or automatic model downloads. The model card is https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 .

```sh
python archive.py fictional-letters.json 'How was music remembered after moving house?' --cache /absolute/path/to/model-cache
python -m unittest -v
python evaluate.py --cache /absolute/path/to/model-cache --output evaluation.json
python server.py --cache /absolute/path/to/model-cache
```

Open http://127.0.0.1:8798 . The server binds only to loopback, serves only the explicit UI assets and fictional letters, checks Host and Origin, and does not log questions. This local demo is not an internet deployment. Select any retrieved passage to highlight its exact source context. Three example buttons include a known model failure and an unanswerable query. This Python-backed interface uses the supplied fictional archive. The static browser edition below additionally supports local text-file import.

Each source document has a unique `id` and `text`. Newline-delimited passages preserve exact character offsets and a SHA-256 of the entire source text. Long passages and queries are rejected above 256 model tokens instead of silently truncated. Only 1–200 nonempty passages are accepted. Input files should be material you are entitled to process. The CLI prints the retrieved text; avoid sending private logs to public hosting.

## What the score means

Mean-pooled, normalized MiniLM embeddings are compared with cosine similarity. Up to three candidate passages are returned even when none passes the provisional 0.4 threshold. That threshold is an interface cue, not an accuracy, truth or absence guarantee. High similarity cannot establish an answer; low similarity cannot prove that a memory is missing. The user reads the original passage.

## Observed limitations

A six-case fictional development run blocked socket connections and still loaded the cached model and returned results. For four related queries the top-ranked document matched the intended document in three cases. An indirect question about waiting for someone to return instead ranked a factory-closure passage first. Only one related query passed the provisional threshold. Two unrelated questions stayed below it. These are tiny development examples, not independent accuracy or user research. No threshold has been tuned to make the examples pass.

This English encoder is not validated for Korean or multilingual archives. It does not resolve negation, contradictory memories, historical truth, writer intent or missing facts. The demonstration contains no actual family history. Stronger relevance evaluation and usability research remain future work.

## Static browser edition

The `docs/` directory is a standalone static app, suitable for a static host. To test it without Python model dependencies:

```sh
python3 -m http.server 8799 --bind 127.0.0.1 --directory docs
```

Open http://127.0.0.1:8799 . Search starts Transformers.js 2.17.2 and the quantized Apache-2.0 Xenova/all-MiniLM-L6-v2 conversion inside the browser. First use downloads library/model files from jsDelivr and Hugging Face (approximately 50 MB). Questions and imported text are processed in browser memory, not sent to an inference API. Hosting and model providers still receive normal page/file requests. Browser cache persistence and offline reload are not guaranteed.

You can load your own English `.txt` file up to 20 KB and 200 nonempty lines. The file is read locally; each line is a passage. Restore fictional letters to return to the demonstration. Changing archives invalidates the embedding index. Model token limits are checked before inference. Reloading clears imported text.

Observed native-browser checks: music query and source switching; low-score last-words query; import of a separate fictional two-line text; retrieving its orange-mailing sentence (cosine 0.593); rejection of a 300-token question; restoration of the original archive. Browser quantization returned different scores from the Python reference, so the Python evaluation is not a browser benchmark. Mobile layout has not yet been verified.
