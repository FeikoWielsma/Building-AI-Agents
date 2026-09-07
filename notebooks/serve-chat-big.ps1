# serve-chat-big.ps1 — OPTIONAL: Qwen3.6-35B-A3B MoE from your local cache on :8000
# ~21 GB model. Only run this with most apps CLOSED (needs ~13 GB free RAM on top
# of the GPU). Slower than serve-chat.ps1 (the 9B) — for experimentation, not live demos.
# Stop the 9B server first so it isn't holding VRAM.
$MODEL = "C:\Users\feiko\.cache\huggingface\hub\models--unsloth--Qwen3.6-35B-A3B-MTP-GGUF\snapshots\5bc3e238d916f48a861bac2f8a1990a0e9b7e98d\Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf"
$LLAMA = "C:\Git\llama.cpp\build\bin\Release\llama-server.exe"

# Chat template: froggeric's fixed template (same file works for 3.5 and 3.6).
$TEMPLATE = "$PSScriptRoot\chat_template.jinja"

& $LLAMA `
  -m "$MODEL" `
  --host 127.0.0.1 --port 8000 `
  -ngl 99 -ot "exps=CPU" `
  -c 8192 -fa on `
  --jinja --chat-template-file "$TEMPLATE" `
  --reasoning off `
  $args

# To revert to the model's built-in template, drop `--chat-template-file "$TEMPLATE"`
# above so the line reads just `--jinja `.

# -ot "exps=CPU"  keeps the MoE expert tensors in system RAM and puts the rest on the GPU.
# If it still won't fit / pages badly, lower -ngl (e.g. 20) or reduce -c.
