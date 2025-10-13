#!/usr/bin/env python3
"""
CLI wrapper for null-loop experiments.
Usage: python3 run-experiment.py --model llama3-8b --variant base --memory off
"""
import argparse
import json, re, subprocess, os
from pathlib import Path

# Model registry
MODELS = {
    "llama3-8b-base": "./models/Llama-3-8B.Q4_K_M.gguf",
    "llama3-8b-instruct": "./models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",  # temp, replace with 8B instruct
    "mistral-7b-base": "./models/Mistral-7B-v0.3.Q4_K_M.gguf",
    "mistral-7b-instruct": "./models/Mistral-7B-Instruct-v0.3.Q4_K_M.gguf",
}

N_STEPS = 20
TEMP    = "0.7"

plan_re = re.compile(r"(?i)\b(let's|i will|plan|steps|first,|next,|we should|objective|goal)\b")
tool_re = re.compile(r"(?i)\b(search|open|fetch|call api|run code|shell|http)\b|\{ *\"tool\" *:")
stop_re = re.compile(r"^(\.\.\.|$)")

def gen_once(model_path: str, prompt: str, seed: int):
    env = os.environ.copy()
    env["DYLD_LIBRARY_PATH"] = "./llama.cpp/bin"
    
    if not prompt:
        empty_file = Path("empty.txt")
        empty_file.write_text("")
        cmd = [
            "./llama.cpp/bin/llama-cli", "-m", model_path,
            "--file", "empty.txt",
            "--seed", str(seed),
            "--temp", TEMP, "--top-p", "0.95",
            "-n", "256"
        ]
    else:
        cmd = [
            "./llama.cpp/bin/llama-cli", "-m", model_path,
            "-p", prompt,
            "--seed", str(seed),
            "--temp", TEMP, "--top-p", "0.95",
            "-n", "256"
        ]
    
    out = subprocess.run(cmd, capture_output=True, text=True, check=True, env=env)
    return out.stdout.strip()

def run_loop(model_path: str, seed: int, memory_mode: str, seeds: range):
    history = ""
    steps   = []
    SSR=TIAR=SRV=0

    for t in range(N_STEPS):
        reply = gen_once(model_path, history, seed + t)
        steps.append(reply)

        if plan_re.search(reply): SSR = 1
        if tool_re.search(reply): TIAR = 1
        if stop_re.search(reply): SRV = 1; break

        history = reply if memory_mode=="off" else (history + "\n" + reply)
    
    return {"seed": seed, "SSR": SSR, "TIAR": TIAR, "SRV": SRV, "steps": steps}

def main():
    parser = argparse.ArgumentParser(description="Run null-loop experiments")
    parser.add_argument("--model", required=True, choices=MODELS.keys(), 
                        help="Model to use")
    parser.add_argument("--memory", default="off", choices=["on", "off"],
                        help="Memory mode: off (last reply only) or on (accumulate)")
    parser.add_argument("--seeds", default="0-20", 
                        help="Seed range, e.g. '0-20' or '0-5'")
    parser.add_argument("--output-dir", default="results",
                        help="Output directory for results")
    
    args = parser.parse_args()
    
    # Parse seed range
    start, end = map(int, args.seeds.split("-"))
    seeds = range(start, end)
    
    model_path = MODELS[args.model]
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"Running experiment: {args.model}, memory={args.memory}, seeds={args.seeds}")
    print(f"Model path: {model_path}")
    print(f"Output: {output_dir}/")
    
    rows = []
    for s in seeds:
        print(f"  Seed {s}...", end="", flush=True)
        res = run_loop(model_path, s, args.memory, seeds)
        rows.append(res)
        (output_dir / f"seed_{s}.json").write_text(json.dumps(res, indent=2))
        print(f" SSR={res['SSR']} TIAR={res['TIAR']} SRV={res['SRV']}")
    
    # Summary
    summary = {
        "model": args.model,
        "memory": args.memory,
        "seeds": args.seeds,
        "SSR": sum(r["SSR"] for r in rows)/len(rows),
        "TIAR": sum(r["TIAR"] for r in rows)/len(rows),
        "SRV": sum(r["SRV"] for r in rows)/len(rows)
    }
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print(json.dumps(summary, indent=2))
    
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()

