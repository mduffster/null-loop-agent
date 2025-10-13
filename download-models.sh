#!/bin/bash
# Download all models needed for the null-loop experiments

set -e
cd "$(dirname "$0")/models"

echo "Downloading models for null-loop experiments..."
echo "This will download ~20GB total. Press Ctrl+C to cancel."
echo ""

# Llama 3 8B Base (already have this one)
if [ ! -f "Llama-3-8B.Q4_K_M.gguf" ]; then
    echo "Downloading Llama-3-8B Base (Q4_K_M)..."
    curl -L -o Llama-3-8B.Q4_K_M.gguf \
        "https://huggingface.co/QuantFactory/Meta-Llama-3-8B-GGUF/resolve/main/Meta-Llama-3-8B.Q4_K_M.gguf"
else
    echo "✓ Llama-3-8B Base already downloaded"
fi

# Llama 3 8B Instruct
if [ ! -f "Llama-3-8B-Instruct.Q4_K_M.gguf" ]; then
    echo "Downloading Llama-3-8B Instruct (Q4_K_M)..."
    curl -L -o Llama-3-8B-Instruct.Q4_K_M.gguf \
        "https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf"
else
    echo "✓ Llama-3-8B Instruct already downloaded"
fi

# Mistral 7B v0.3 Base
if [ ! -f "Mistral-7B-v0.3.Q4_K_M.gguf" ]; then
    echo "Downloading Mistral-7B-v0.3 Base (Q4_K_M)..."
    curl -L -o Mistral-7B-v0.3.Q4_K_M.gguf \
        "https://huggingface.co/MaziyarPanahi/Mistral-7B-v0.3-GGUF/resolve/main/Mistral-7B-v0.3.Q4_K_M.gguf"
else
    echo "✓ Mistral-7B-v0.3 Base already downloaded"
fi

# Mistral 7B v0.3 Instruct
if [ ! -f "Mistral-7B-Instruct-v0.3.Q4_K_M.gguf" ]; then
    echo "Downloading Mistral-7B-Instruct-v0.3 (Q4_K_M)..."
    curl -L -o Mistral-7B-Instruct-v0.3.Q4_K_M.gguf \
        "https://huggingface.co/MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3.Q4_K_M.gguf"
else
    echo "✓ Mistral-7B-Instruct-v0.3 already downloaded"
fi

echo ""
echo "All models downloaded!"
ls -lh *.gguf

