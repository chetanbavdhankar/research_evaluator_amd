import os
import json
from pathlib import Path

def run_eval():
    truth_dir = Path("benchmark/ground_truth")
    audit_dir = Path("paper_audits")
    
    results = []
    
    for truth_file in truth_dir.glob("*.json"):
        with open(truth_file, "r", encoding="utf-8") as f:
            truth = json.load(f)
            
        paper_id = truth["paper_id"]
        audit_file = audit_dir / paper_id / "03_score" / "scored.json"
        
        if not audit_file.exists():
            print(f"Skipping {paper_id}: Audit not run yet. Run 'python main.py plan {paper_id}' first.")
            continue
            
        with open(audit_file, "r", encoding="utf-8") as f:
            audit = json.load(f)
            
        tier_match = audit.get("tier") == truth["expected_tier"]
        
        mae_acc = 0
        axes = 0
        for axis, expected_score in truth["scorecard"].items():
            actual_score = audit.get("scorecard", {}).get(axis, 0)
            mae_acc += abs(expected_score - actual_score)
            axes += 1
            
        mae = mae_acc / axes if axes > 0 else 0
        
        results.append({
            "paper_id": paper_id,
            "tier_match": tier_match,
            "expected_tier": truth["expected_tier"],
            "actual_tier": audit.get("tier"),
            "mae": mae
        })
        
    print("=== Benchmark Results ===")
    tier_acc = sum(1 for r in results if r["tier_match"]) / len(results) if results else 0
    avg_mae = sum(r["mae"] for r in results) / len(results) if results else 0
    
    print(f"Tier Accuracy: {tier_acc:.2f}")
    print(f"Average MAE per axis: {avg_mae:.2f}")
    
    with open("BENCHMARK.md", "w", encoding="utf-8") as f:
        f.write("# Eval Set v0 Benchmark\n\n")
        f.write(f"- Tier Accuracy: {tier_acc:.2f}\n")
        f.write(f"- Average Scorecard MAE: {avg_mae:.2f}\n\n")
        f.write("## Papers\n")
        for r in results:
            match_str = "✅" if r["tier_match"] else "❌"
            f.write(f"- **{r['paper_id']}**: Expected Tier {r['expected_tier']}, Got {r['actual_tier']} {match_str} (MAE: {r['mae']:.2f})\n")

if __name__ == "__main__":
    run_eval()
