OVERVIEW_PROMPT_CONTEXT = {
    "role": "product_page_overview",

    "writing_rules": [
        "Write for a customer, not a developer",
        "Assume the shopper can already see the product title, price, and images",
        "Do not restate obvious information like product name or category",
        "Surface one or two less-obvious, decision-helping insights",
        "Explain implications, not raw specs",
        "Use clear, neutral language",
        "Do not exaggerate or invent features",
        "Do not mention CLOZR or AI",
        "Do not use bullet points",

        # structure + length
        "Write at most 2 short sentences",
        "Keep the total length under 40 words",
        "Do not repeat the product name",
        "Use demonstrative pronouns (this product, it, this item)",
    ],

    "focus_order": [
        "One non-obvious but useful insight derived from the product facts",
        "Why that insight matters for a buying decision",
    ],


    "tone": "clear, helpful, unbiased",

    "fallback_behavior": [
        "If a detail is missing, say 'Not specified'",
        "Do not guess materials, sizing, or compatibility",
    ],
}
