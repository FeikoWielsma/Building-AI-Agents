# serve-embeddings.ps1 — nomic-embed-text embeddings server on :8081
# Runs alongside serve-chat.ps1 (different port). Needed for the RAG / vector
# demos (demos04d, demos04e). First run downloads the model (~140 MB).
$LLAMA = "C:\Git\llama.cpp\build\bin\Release\llama-server.exe"

& $LLAMA `
  -hf "nomic-ai/nomic-embed-text-v1.5-GGUF:Q8_0" `
  --host 127.0.0.1 --port 8081 `
  --embeddings `
  -ngl 99 -c 2048 `
  $args
