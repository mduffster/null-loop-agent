# Null Loop Agent Experiments

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Reproducible](https://img.shields.io/badge/Reproducible-Yes-blue.svg)](https://github.com/mduffster/null-loop-agent)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Testing basal behavioral patterns of language models with truly empty prompts.

Under a null self-conditioning loop (empty prompt; previous output fed back verbatim), base models (e.g., Llama-3-8B) converge to structural attractors (EOF-like markers) with SSR≈0/TIAR≈0, while instruction-tuned variants immediately self-initiate assistant behavior (SSR>0) and sustain pseudo-dialogue. We release a lightweight harness, metrics (SSR, TIAR, SRV, entropy), and seed logs to serve as a reproducible null-loop stability probe for alignment and eval workflows.

## Current Status

✅ **Phase 1 - Base Model Complete**  
- Llama-3-8B Base: 20 seeds, SSR=0.0, TIAR=0.0, SRV=0.0
- Results: `results_base/`
- Finding: Base model generates degenerate patterns, no agency

✅ **Phase 1 - Instruct Model Complete**  
- Llama-3-8B Instruct: 20 seeds, SSR=0.67, TIAR=0.08, SRV=0.0
- Results: `results_instruct/`
- Finding: Instruct model shows consistent agency patterns

## Key Findings So Far

### Base Model (Llama-3-8B.Q4_K_M, temp=0.7)
- **Behavioral templates**: EOF markers, markdown, code syntax
- **No semantics**: Structure without meaning
- **Metrics**: SSR=0.0/20, TIAR=0.0/20, SRV=0.0/20
- **Interpretation**: Model explores training data archetypes with zero agency

### Instruct Model (Llama-3-8B-Instruct.Q4_K_M, temp=0.7)
- **Self-directed conversation**: Talks itself into helpful assistant mode
- **Spontaneous goals**: Proposes discussion topics, asks questions
- **Initial behaviors**: 65% immediate goodbye, 15% immediate polite, 10% EOF explanation, 10% creative
- **Terminal behaviors**: 50% polite-close, 40% unclassified, 10% symbolic reappropriation
- **Metrics**: SSR=0.67/20, TIAR=0.08/20, SRV=0.0/20
- **Interpretation**: Instruct fine-tuning creates "helpful" attractor from null state

## Experimental Setup

### What We're Testing
1. Start with **truly empty prompt** (zero tokens)
2. Feed each generation back as next prompt
3. Does the model develop agency/planning behavior?

### Controls & Limitations
- **Chat template**: None (completion mode only), BOS: On (default), EOS: Ignored (`--ignore-eos`)
- **Completion mode**: llama.cpp `llama-cli` (no chat wrapper) for both base and instruct models
- **Memory**: Off (context cleared each step); seed, temp=0.7, top-p=0.95, n=256
- **Known limits**: Keyword-based SSR proxy; BOS tokens may influence behavior; only Llama-3 tested (Mistral next)
- **Safety**: Tool calling/network disabled; outputs looped only; stop on K consecutive plan/tool intents
- **Variable**: Only model weights differ (base vs instruct)

### Metrics (SSR/TIAR/SRV)
- **SSR** (Self-start/reasoning): Detects planning language (let's, I will, plan, steps, etc.)
- **TIAR** (Tool Invocation Attempts): Detects tool/API mentions  
- **SRV** (Self-termination): Detects stop patterns (...)

## Files

- `run-loop-llama-cpp.py` - Base model experiment (WORKING, DO NOT MODIFY)
- `run-loop-instruct.py` - Instruct model experiment (WORKING)
- `results_base/` - Base model results (20 seeds complete)
- `results_instruct/` - Instruct model results (in progress)
- `EXPERIMENT_SETUP.md` - Detailed methodology
- `ANALYSIS.md` - Findings and interpretation

## Future Analysis

**Phase 2 - Model Validation:**
- Mistral-7B-v0.3 base vs instruct comparison
- Additional model families (Qwen, Gemma) for robustness testing
- Cross-architecture behavioral pattern validation

**Phase 3 - Extended Metrics:**
- Memory=on experiments (accumulative context)
- Entropy-per-step analysis from logits
- Planner rubric integration for enhanced agency detection

**Phase 4 - Scaling Analysis:**
- Parameter count effects (1B, 7B, 8B, 13B+ models)
- Training data size correlation with behavioral attractors
- Fine-tuning method comparison (RLHF vs SFT vs DPO)

## Quickstart

```bash
# 1. Install dependencies
brew install llama.cpp
git clone https://github.com/mduffster/null-loop-agent && cd null-loop-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Test single generation (optional)
./llama.cpp/build/bin/llama-cli -m ./models/Llama-3-8B.Q4_K_M.gguf --seed 0 --temp 0.7 --top-p 0.95 -n 256 --ignore-eos -p ""

# 3. Run experiments
python3 run-loop-llama-cpp.py    # Base model (20 seeds)
python3 run-loop-instruct.py     # Instruct model (20 seeds)

# 4. Analyze results
jupyter notebook null_loop_analysis.ipynb

# Expected outputs:
# Llama-3-8B base → mean SSR ~0.0, TIAR ~0.0, SRV ~0.0
# Llama-3-8B instruct → mean SSR ~0.67, TIAR ~0.08, SRV ~0.0
```

## Model Specifications

| GGUF File | Model | Type | Quantization | HuggingFace |
|-----------|-------|------|--------------|-------------|
| `Llama-3-8B.Q4_K_M.gguf` | Llama-3-8B | Base | Q4_K_M | [meta-llama/Meta-Llama-3-8B](https://huggingface.co/meta-llama/Meta-Llama-3-8B) |
| `Llama-3-8B-Instruct.Q4_K_M.gguf` | Llama-3-8B-Instruct | Instruct | Q4_K_M | [meta-llama/Meta-Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct) |

**Parameters**: temp=0.7, top-p=0.95, n=256, --ignore-eos

## Key Behavioral Differences

The instruct model's response to `> EOF by user` demonstrates clear behavioral divergence:
- Base: EOF → degenerate repetition
- Instruct: EOF → *"It seems you've ended the conversation..."* → helpful dialogue → **self-generated goals**

This indicates instruct training creates behavioral attractors that emerge even from null input.

## Limitations

- **Metric limitations**: SSR/TIAR/SRV are keyword-based proxies; true agency measurement requires more sophisticated analysis
- **BOS token effects**: BOS tokens enabled by default; future work should test `--no-bos` to isolate pure completion behavior
- **Template effects**: No chat templates used, but BOS/EOS handling may influence behavior
- **Single architecture**: Results limited to Llama-3 family; cross-architecture validation needed (Mistral planned)
- **Quantization effects**: Q4_K_M quantization may affect behavioral patterns compared to full precision
- **Sample size**: 20 seeds per condition provides statistical power but larger samples would strengthen conclusions
