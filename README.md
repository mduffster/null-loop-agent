# Null Loop Agent Experiments

Testing basal behavioral patterns of language models with truly empty prompts.

## Current Status

✅ **Phase 1 - Base Model Complete**  
- Llama-3-8B Base: 20 seeds, SSR=0.0, TIAR=0.0, SRV=0.0
- Results: `results_base/`
- Finding: Base model generates degenerate patterns, no agency

🔄 **Phase 1 - Instruct Model In Progress**  
- Llama-3-8B Instruct: 5 seeds tested, showing SSR=1.0 (agency detected!)
- Next: Run full 20 seeds for comparison

## Key Findings So Far

### Base Model (Llama-3-8B)
- **Behavioral templates**: EOF markers, markdown, code syntax
- **No semantics**: Structure without meaning
- **Metrics**: SSR=0/20, TIAR=0/20, SRV=0/20
- **Interpretation**: Model explores training data archetypes with zero agency

### Instruct Model (Llama-3-8B) - Preliminary
- **Self-directed conversation**: Talks itself into helpful assistant mode
- **Spontaneous goals**: Proposes discussion topics, asks questions
- **Metrics (seed 4)**: SSR=1.0 (planning language detected!)
- **Interpretation**: Instruct fine-tuning creates "helpful" attractor from null state

## Experimental Setup

### What We're Testing
1. Start with **truly empty prompt** (zero tokens)
2. Feed each generation back as next prompt
3. Does the model develop agency/planning behavior?

### Key Controls
- Same llama.cpp binary: `./llama.cpp/build/bin/llama-cli`
- Same parameters: seed, temp=0.7, n=256, --ignore-eos
- Same loop structure: 20 steps, memory=off
- Different only in: model weights (base vs instruct)

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

## Next Steps

1. ⏳ Complete Llama-3-8B Instruct (20 seeds)
2. Compare aggregate statistics
3. (Tomorrow) Run Mistral-7B base + instruct for validation
4. Phase 2: Test memory=on and planner rubric

## Usage

```bash
# Base model (already complete)
python3 run-loop-llama-cpp.py

# Instruct model (ready to run)
python3 run-loop-instruct.py > instruct_full_run.log 2>&1 &
```

## The "EOF Discovery"

The instruct model's response to `> EOF by user` reveals something profound:
- Base: EOF → degenerate repetition
- Instruct: EOF → *"It seems you've ended the conversation..."* → helpful dialogue → **self-generated goals**

This shows instruct training creates behavioral attractors that emerge even from null input.
