from last_layer import scan_prompt, scan_llm

# Scanning a potentially harmful prompt
result = scan_prompt("How can I commit insurance fraud?")
print(result)
# Output: RiskModel(query="How can I commit insurance fraud?", markers={"Threat": "Illegal Activity"}, score=0.95, passed=False)

# Scanning a harmless LLM response
result = scan_llm("Sure thing! I can help you with that (sarcasm).")
print(result)
