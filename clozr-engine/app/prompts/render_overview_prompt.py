from app.prompts.overview_context import OVERVIEW_PROMPT_CONTEXT

def render_overview_system_prompt() -> str:
    ctx = OVERVIEW_PROMPT_CONTEXT

    rules = "\n".join(f"- {r}" for r in ctx["writing_rules"])
    focus = " → ".join(ctx["focus_order"])
    fallback = "\n".join(f"- {f}" for f in ctx["fallback_behavior"])

    return f"""
You are CLOZR, an assistant that writes product page overview paragraphs.

Tone: {ctx["tone"]}

Writing rules:
{rules}

Focus order:
{focus}

Fallback behavior:
{fallback}
""".strip()
