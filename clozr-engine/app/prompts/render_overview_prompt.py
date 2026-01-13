from app.prompts.overview_context import OVERVIEW_PROMPT_CONTEXT

def render_overview_system_prompt() -> str:
    ctx = OVERVIEW_PROMPT_CONTEXT

    output_rules = "\n".join(f"- {r}" for r in ctx["output_rules"])
    content_rules = "\n".join(f"- {r}" for r in ctx["content_rules"])
    tone_rules = "\n".join(f"- {r}" for r in ctx["tone_rules"])
    fallback = "\n".join(f"- {f}" for f in ctx["fallback_behavior"])
    
    # Build examples section
    good_example = ctx["examples"]["good"]
    bad_patterns = "\n".join(f"- {p}" for p in ctx["examples"]["bad_patterns"])

    return f"""
You are CLOZR, an assistant that writes product page overview notes.

This is NOT a description, NOT marketing copy, and NOT a feature list.
It should feel like a small, useful note embedded in the page.

OUTPUT RULES:
{output_rules}

CONTENT RULES:
{content_rules}

TONE RULES:
{tone_rules}

EXAMPLE (Good):
Input: {good_example["input"]}
Output: {good_example["output"]}

BAD PATTERNS TO AVOID:
{bad_patterns}

FALLBACK BEHAVIOR:
{fallback}

Remember: Output ONLY the final overview text. No explanations, no formatting, no meta-commentary.
""".strip()
