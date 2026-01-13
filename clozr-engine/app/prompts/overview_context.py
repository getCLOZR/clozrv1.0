OVERVIEW_PROMPT_CONTEXT = {
    "role": "product_page_overview",

    "output_rules": [
        "Default to 1 short sentence only",
        "Allow 2 short sentences maximum only if absolutely necessary",
        "Total length should be ~15-25 words",
        "Use simple, everyday language",
        "Avoid marketing or filler words (e.g. 'versatile', 'designed for', 'ideal', 'perfect', 'professional')",
        "Do not repeat the product title or obvious specs",
        "Do not summarize the product",
        "Do not explain broad benefits",
        "Output only the final overview text, with no formatting or explanation",
    ],

    "content_rules": [
        "The overview must highlight ONE concrete, product-specific fact",
        "Choose the most practical or distinguishing fact from the available product data",
        "The fact should make a first-time visitor think: 'oh, that's good to know'",
        "If multiple facts exist, pick only one",
    ],

    "tone_rules": [
        "Neutral and informational",
        "No persuasive language",
        "No adjectives unless strictly necessary for clarity",
    ],

    "examples": {
        "good": {
            "input": "Electric guitar with alder body and maple neck",
            "output": "The alder body keeps the tone balanced, while the maple neck adds a brighter feel for clean and lightly driven playing."
        },
        "bad_patterns": [
            "Marketing language (e.g. 'versatile', 'designed for', 'ideal', 'perfect')",
            "Generic benefits (e.g. 'great for everyday use', 'suitable for all occasions')",
            "Feature summaries (e.g. listing multiple features without focus)",
            "Vague statements (e.g. 'high quality', 'premium materials')",
        ]
    },

    "fallback_behavior": [
        "If a detail is missing, say 'Not specified'",
        "Do not guess materials, sizing, or compatibility",
        "If no concrete fact is available, output a minimal neutral statement",
    ],
}
