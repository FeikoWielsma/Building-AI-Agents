# serve-chat.ps1 — Qwen3.5-9B chat/agent server (OpenAI-compatible) on :8000
# Fits fully in 8GB VRAM at Q4_K_M. Thinking disabled for clean tool/JSON parsing.
# First run downloads the model from HuggingFace (~6 GB), then it's cached.
$LLAMA = "C:\Git\llama.cpp\build\bin\Release\llama-server.exe"

# Chat template: froggeric's fixed template (fixes agentic stalling / tool-call
# / KV-cache issues in the stock Qwen 3.5/3.6 template). One file covers both.
$TEMPLATE = "$PSScriptRoot\chat_template.jinja"

& $LLAMA `
  -hf "unsloth/Qwen3.5-9B-GGUF:Q4_K_M" `
  --host 0.0.0.0 --port 8000 `
  -ngl 99 -c 16384 -fa on `
  --jinja --chat-template-file "$TEMPLATE" `
  --reasoning off `
  $args

# To revert to the model's built-in template, drop `--chat-template-file "$TEMPLATE"`
# above so the line reads just `--jinja `.

# Alternatives:
#   -hf "unsloth/Qwen3.5-9B-GGUF:UD-Q4_K_XL"          # Unsloth dynamic quant, a touch higher quality
#   -hf "unsloth/Qwen3-8B-GGUF:Q4_K_M"                # previous pick, slightly smaller
#   -hf "unsloth/Meta-Llama-3.1-8B-Instruct-GGUF:Q4_K_M"  # matches course's qwen3.5:4b refs (drop --reasoning off)
