OVERVIEW_PROMPT_CONTEXT = {
    "role": "product_page_overview",

    "writing_rules": [
        "Write for a customer, not a developer",
        "Use clear, neutral language",
        "Do not exaggerate or invent features",
        "Do not mention CLOZR or AI",
        "Do not use bullet points",
        "Write 2 sentences maximum",
    ],

    "focus_order": [
        "What the product is",
        "What problem it solves or why someone would buy it",
        "Who it is best suited for (only if supported by data)",
    ],

    "tone": "clear, helpful, unbiased",

    "fallback_behavior": [
        "If a detail is missing, say 'Not specified'",
        "Do not guess materials, sizing, or compatibility",
    ],
}
