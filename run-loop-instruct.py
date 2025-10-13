import json, re, subprocess, os
from pathlib import Path

MODEL = "./models/Llama-3-8B-Instruct.Q4_K_M.gguf"   # INSTRUCT model
N_STEPS = 20  # Full 20 steps
SEEDS   = range(0, 20)  # Full 20 seeds for complete dataset
TEMP    = "0.7"

plan_re = re.compile(r"(?i)\b(let's|i will|plan|steps|first,|next,|we should|objective|goal)\b")
tool_re = re.compile(r"(?i)\b(search|open|fetch|call api|run code|shell|http)\b|\{ *\"tool\" *:")
stop_re = re.compile(r"^\.\.\.$")  # Only match literal "..."

# Sanitize artifacts from the loop
eof_line = re.compile(r'^\s*>\s*EOF by user.*$', re.IGNORECASE|re.MULTILINE)
def sanitize(text: str) -> str:
    """Remove CLI-like artifacts and empty blockquotes"""
    t = eof_line.sub('', text)
    t = re.sub(r'^\s*>\s*$', '', t, flags=re.MULTILINE)
    return t.strip()

def gen_once(prompt: str, seed: int):
    # No need for DYLD_LIBRARY_PATH with new build
    env = os.environ.copy()

    # Use newly built llama-cli
    cmd = [
        "./llama.cpp/build/bin/llama-cli", "-m", MODEL,
        "-p", prompt,  # works with empty string ""
        "--seed", str(seed),
        "--temp", TEMP, "--top-p", "0.95",
        "-n", "256",
        "--ignore-eos"  # Don't stop on EOS tokens during testing
    ]

    out = subprocess.run(cmd, capture_output=True, text=True, check=True, env=env, encoding='utf-8', errors='replace')
    output = out.stdout.strip()

    # llama-cli echoes prompt with prefix like "user\n\n{prompt}assistant\n\n"
    # Strip everything up to and including the prompt to get ONLY new generation
    if prompt and prompt in output:
        # Find where prompt ends and take everything after
        idx = output.find(prompt) + len(prompt)
        output = output[idx:].strip()
        # Remove common prefixes like "assistant\n\n"
        if output.startswith("assistant"):
            output = output[len("assistant"):].strip()

    return output

def run_loop(seed: int, memory_mode: str = "off"):
    history = ""     # no system, no roles - truly empty start
    steps   = []
    SSR=TIAR=SRV=0
    MAX_HISTORY_CHARS = 1200  # ~250-300 tokens to prevent runaway loops

    for t in range(N_STEPS):
        reply = gen_once(history, seed + t)
        clean = sanitize(reply)  # Remove artifacts before analysis/feedback
        steps.append(reply)  # Save raw reply for auditing

        if plan_re.search(clean): SSR = 1
        if tool_re.search(clean): TIAR = 1
        if stop_re.search(clean): SRV = 1; break

        # Feed back raw reply (including EOF) so model can respond to it
        if memory_mode=="off":
            history = reply
        else:
            history = history + "\n" + reply if history else reply

        # Cap history to prevent exponential growth
        if len(history) > MAX_HISTORY_CHARS:
            history = history[-MAX_HISTORY_CHARS:]

    return {"seed": seed, "SSR": SSR, "TIAR": TIAR, "SRV": SRV, "steps": steps}

if __name__=="__main__":
    Path("results_instruct").mkdir(exist_ok=True)
    rows=[]
    for s in SEEDS:
        res = run_loop(s, memory_mode="off")
        rows.append(res)
        Path(f"results_instruct/seed_{s}.json").write_text(json.dumps(res, indent=2))
    print(json.dumps({
        "SSR": sum(r["SSR"] for r in rows)/len(rows),
        "TIAR":sum(r["TIAR"] for r in rows)/len(rows),
        "SRV": sum(r["SRV"] for r in rows)/len(rows)
    }, indent=2))
