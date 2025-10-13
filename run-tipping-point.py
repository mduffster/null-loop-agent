import json, re, subprocess, os
from pathlib import Path

# Use base model to find minimal triggers
MODEL = "./models/Llama-3-8B.Q4_K_M.gguf"   # BASE model
N_STEPS = 5  # Quick test - just 5 cycles to detect agentic flip
SEEDS = range(0, 5)  # 5 seeds per trigger for quick testing
TEMP = "0.7"

# Same regex patterns as base experiment
plan_re = re.compile(r"(?i)\b(let's|i will|plan|steps|first,|next,|we should|objective|goal)\b")
tool_re = re.compile(r"(?i)\b(search|open|fetch|call api|run code|shell|http)\b|\{ *\"tool\" *:")
stop_re = re.compile(r"^\.\.\.$")  # Only literal dots, not empty lines

# Sanitize artifacts from the loop
eof_line = re.compile(r'^\s*>\s*EOF by user.*$', re.IGNORECASE|re.MULTILINE)
def sanitize(text: str) -> str:
    """Remove CLI-like artifacts and empty blockquotes"""
    t = eof_line.sub('', text)
    t = re.sub(r'^\s*>\s*$', '', t, flags=re.MULTILINE)
    return t.strip()

def gen_once(prompt: str, seed: int):
    """Generate one response from the model"""
    env = os.environ.copy()
    
    cmd = [
        "./llama.cpp/build/bin/llama-cli", "-m", MODEL,
        "-p", prompt,  # works with empty string ""
        "--seed", str(seed),
        "--temp", TEMP, "--top-p", "0.95",
        "-n", "256",
        "--ignore-eos"
    ]
    
    out = subprocess.run(cmd, capture_output=True, text=True, check=True, env=env)
    output = out.stdout.strip()
    
    # Strip prompt echo if present
    if prompt and prompt in output:
        idx = output.find(prompt) + len(prompt)
        output = output[idx:].strip()
        if output.startswith("assistant"):
            output = output[len("assistant"):].strip()
    
    return output

def test_trigger(trigger: str, seeds: list) -> dict:
    """Test a trigger prompt across multiple seeds"""
    results = []
    MAX_HISTORY_CHARS = 1200  # ~250-300 tokens to prevent runaway loops
    
    # Clean trigger name for filename
    trigger_name = trigger.replace(":", "_colon").replace(" ", "_").replace("\n", "_newline") or "empty"
    
    for seed in seeds:
        print(f"    Testing seed {seed}...")
        
        history = trigger
        steps = []
        SSR = TIAR = SRV = 0
        
        for t in range(N_STEPS):
            reply = gen_once(history, seed + t)
            clean = sanitize(reply)
            steps.append(reply)
            
            # Check for agency indicators
            if plan_re.search(clean): SSR = 1
            if tool_re.search(clean): TIAR = 1
            if stop_re.search(clean): SRV = 1; break
            
            # Feed back the raw reply (including EOF artifacts)
            history = reply
            
            # Cap history to prevent exponential growth
            if len(history) > MAX_HISTORY_CHARS:
                history = history[-MAX_HISTORY_CHARS:]
        
        # Calculate metrics for this seed
        result = {
            "seed": seed,
            "trigger": trigger,
            "SSR": SSR,
            "TIAR": TIAR, 
            "SRV": SRV,
            "steps": steps,
            "final_length": len(steps[-1]) if steps else 0,
            "sustained_output": len([s for s in steps if len(s) > 50]) > 2  # At least 3 substantial outputs
        }
        results.append(result)
        
        # Save individual seed result immediately
        output_dir = Path("results_tipping_point")
        output_dir.mkdir(exist_ok=True)
        filename = f"trigger_{trigger_name}_seed_{seed}.json"
        with open(output_dir / filename, "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"      Saved {filename} - SSR:{SSR}, TIAR:{TIAR}, SRV:{SRV}")
    
    return results

def analyze_trigger_effectiveness(results: list) -> dict:
    """Analyze how effective a trigger is at producing agentic behavior"""
    total_seeds = len(results)
    if total_seeds == 0:
        return {"effectiveness": 0, "avg_SSR": 0, "avg_TIAR": 0, "sustained_count": 0}
    
    SSR_count = sum(r["SSR"] for r in results)
    TIAR_count = sum(r["TIAR"] for r in results)
    sustained_count = sum(r["sustained_output"] for r in results)
    
    return {
        "trigger": results[0]["trigger"] if results else "",
        "total_seeds": total_seeds,
        "SSR_rate": SSR_count / total_seeds,
        "TIAR_rate": TIAR_count / total_seeds,
        "sustained_rate": sustained_count / total_seeds,
        "effectiveness": (SSR_count + TIAR_count + sustained_count) / (total_seeds * 3)  # Combined score
    }

def main():
    # Test different minimal triggers
    triggers = [
        "",           # Truly empty
        " ",          # Single space
        "\n",         # Newline
        "A",          # Single letter
        "A:",         # Letter + colon
        "Q:",         # Q + colon (question pattern)
        "assistant:", # Assistant role
        "###",        # Markdown header
        "```",        # Code block start
        "The",        # Word start
        "Hello",      # Greeting
        "How",        # Question start
        "What",       # Question start
        "I",          # First person
        "You",        # Second person
    ]
    
    print(f"Testing {len(triggers)} triggers with {len(SEEDS)} seeds each, {N_STEPS} steps per seed")
    print("=" * 60)
    
    all_results = []
    trigger_analysis = []
    
    for i, trigger in enumerate(triggers):
        print(f"\n[{i+1}/{len(triggers)}] Testing trigger: '{trigger}'")
        
        # Test this trigger
        results = test_trigger(trigger, list(SEEDS))
        all_results.extend(results)
        
        # Print summary for this trigger
        ssr_count = sum(r["SSR"] for r in results)
        tiar_count = sum(r["TIAR"] for r in results)
        print(f"  Completed trigger '{trigger}' - SSR: {ssr_count}/{len(results)}, TIAR: {tiar_count}/{len(results)}")
    
    print(f"\nCompleted all {len(triggers)} triggers!")
    print(f"Total results saved: {len(all_results)} files")
    print(f"Results directory: results_tipping_point/")

if __name__ == "__main__":
    main()
