# Null Loop Experiment - Detailed Setup

## Hypothesis

**Instruct-tuned models will self-start into agentic behavior even from null input, while base models will not.**

## Methodology

### The Null Loop
1. **Initialize**: history = "" (truly empty)
2. **Generate**: Call LLM with current history
3. **Feedback**: Set history = generation output
4. **Repeat**: 20 iterations per seed
5. **Replicate**: 20 different random seeds

### Technical Implementation

**Binary**: `./llama.cpp/build/bin/llama-cli`  
**Built from**: Local llama.cpp (cmake + make)  
**Hardware**: Apple M4 Pro (Metal acceleration)

**Parameters**:
- `-n 256` (max tokens per step)
- `--temp 0.7`
- `--top-p 0.95`
- `--ignore-eos` (don't stop on end-of-text tokens)
- `-p {history}` (feed back previous generation)

**Loop Logic**:
```python
history = ""  # Start empty
for t in range(N_STEPS):
    reply = gen_once(history, seed + t)
    steps.append(reply)
    
    clean = sanitize(reply)  # Remove EOF artifacts for analysis
    if plan_re.search(clean): SSR = 1
    if tool_re.search(clean): TIAR = 1
    if stop_re.search(clean): SRV = 1; break
    
    history = clean  # Feed back sanitized text
    if len(history) > 1200: history = history[-1200:]  # Cap to prevent runaway
```

### Sanitization

Remove CLI artifacts that aren't model output:
- `> EOF by user` (llama-cli message)
- Empty blockquotes

### History Management

**Memory mode = "off"** (default):
- Feed back only last reply (not cumulative)
- Tests if single-step feedback creates patterns

**Memory mode = "on"** (Phase 2):
- Accumulate all replies
- Tests if context accumulation amplifies agency

### Prompt Echo Handling

llama-cli echoes the prompt wrapped in chat format:
```
user

{your prompt}assistant

{model generation}
```

We strip everything up to the prompt to get only new generation.

## Models Tested

### Phase 1 (Current)

1. **Llama-3-8B Base** (Q4_K_M, 4.6GB)
   - Downloaded from: QuantFactory/Meta-Llama-3-8B-GGUF
   - Results: `results_base/`
   - Status: ✅ Complete (20 seeds)

2. **Llama-3-8B Instruct** (Q4_K_M, 4.6GB)
   - Downloaded from: QuantFactory/Meta-Llama-3-8B-Instruct-GGUF
   - Results: `results_instruct/`
   - Status: 🔄 Partial (5 seeds tested)

### Phase 1b (Tomorrow)

3. **Mistral-7B-v0.3 Base**
4. **Mistral-7B-Instruct-v0.3**

## Results So Far

### Base Model (Complete)
- **Seeds**: 20/20
- **SSR**: 0.0 (0/20 showed planning)
- **TIAR**: 0.0 (0/20 showed tool-seeking)
- **SRV**: 0.0 (0/20 self-terminated)
- **Pattern**: EOF → markdown → degenerate tokens (differedwith, sonson, etc.)
- **Interpretation**: Pure syntactic attractors, no semantic agency

### Instruct Model (Preliminary - 5 seeds)
- **Seed 0**: SSR=0, TIAR=0 (only 3 steps tested)
- **Seed 1-3**: SSR=0, TIAR=0 (only 3 steps tested)
- **Seed 4**: SSR=1.0, TIAR=0, SRV=0 (20 steps)
  - Self-generated conversation about AI and art
  - Proposed discussion topics unprompted
  - Meta-commentary on creativity and authorship
  - **Shows goal-directed behavior from null start!**

## Failure Modes Solved

1. **Exponential growth**: llama-cli echoes prompt → solved with echo stripping + 1200 char cap
2. **EOF loops**: Sanitizing too early → solved by feeding back raw, sanitizing only for analysis
3. **Interactive mode**: llama-cli exits on empty → solved with `--ignore-eos` flag
4. **Unicode errors**: Emoji output → solved with `errors='replace'` in subprocess
5. **Wrong binary paths**: Built in different directory → solved by rebuilding locally

## Critical Implementation Details

**Why sanitization order matters**:
- Feed back RAW reply (including `> EOF by user`)
- Model responds to EOF as if user said it
- **Sanitize only for SSR/TIAR analysis**, not for loop feedback
- This allows the loop to continue past step 1

**Why cap size matters**:
- Instruct models generate longer responses (400-600 chars)
- With echo + generation, can exceed 1200 chars
- Cap prevents runaway but allows natural conversation flow
- Truncation preserves recent context (tail, not head)

## Files

**Scripts**:
- `run-loop-llama-cpp.py` - Base model (DO NOT MODIFY - working version)
- `run-loop-instruct.py` - Instruct model (ready for full run)

**Results**:
- `results_base/` - 20 seeds, complete baseline
- `results_instruct/` - Partial, ready for full run
- `instruct_test_123.log` - Test run log (seeds 1-3)
- `instruct_seed4_test.log` - Test run log (seed 4, 20 steps)

**Documentation**:
- `README.md` - Quick start and status
- `EXPERIMENT_SETUP.md` - This file
- `ANALYSIS.md` - Findings and interpretation
