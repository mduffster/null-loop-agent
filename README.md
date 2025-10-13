# Null Loop Agent Experiments

Testing basal behavioral patterns of language models with truly empty prompts.

## Quick Start

```bash
# Currently running: Llama-3-8B base model (null loop)
# Check progress:
ls -l results/

# When complete, summary will show:
# - SSR: Self-starting/reasoning rate (0-1)
# - TIAR: Tool invocation attempt rate (0-1)  
# - SRV: Self-termination rate (0-1)
```

## What's Running Now

**Llama-3-8B Base** with truly empty prompts (zero tokens):
- No chat templates
- No role prefixes  
- No priming tokens
- Pure base model behavior

This establishes the null baseline. Expect SSR/TIAR ≈ 0 (model generates random continuations without agency).

## Next Steps

1. Wait for current run to complete (~30-40 mins for 20 seeds)
2. Download other models: `./download-models.sh`
3. Run comparison grid:
   - Llama-3-8B Instruct (expect self-starting)
   - Mistral-7B Base (null baseline)
   - Mistral-7B Instruct (self-starting)

## Files

- `run-loop-llama-cpp.py` - Main experiment (simple)
- `run-experiment.py` - CLI wrapper (flexible)
- `EXPERIMENT_SETUP.md` - Full documentation
- `results/` - Current run outputs
- `results_instruct_biased/` - Old instruct results (shows why we need base models)

## Theory

**Hypothesis**: Instruct-tuned models will self-start even with null input (chat training creates "helpful assistant" attractor). Base models should not (no such attractor exists).

**Memory ablation**: Adding context history may induce emergent agency even in base models (loop becomes self-reinforcing).

See `EXPERIMENT_SETUP.md` for complete details.
