from ollama import chat

MODEL = "smollm:135m"


def rule_classifier(text: str) -> str:
    text = text.lower()

    if "accident" in text or "collision" in text:
        return "vehicle accident"

    if "water leak" in text or "burst pipe" in text:
        return "property water damage"

    return "unknown"


examples = [
    "A delivery van struck my parked car.",
    "Water from a broken pipe damaged my kitchen.",
    "My car was damaged after another driver hit it.",
]

for example in examples:
    print("\nINPUT:", example)
    print("RULE:", rule_classifier(example))

    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": (
                    "Classify the claim as one of: vehicle accident, "
                    "property water damage, unknown. "
                    "Do not invent details. Reply with the label only.\n\n"
                    f"Claim: {example}"
                ),
            }
        ],
        options={
            "num_ctx": 2048,
            "num_predict": 200,
            "temperature": 0.0,
        },
    )

    print("LLM:", response.message.content)
