# Phase 1 - Generative AI Foundations: Answers

Model: `smollm:135m` (Ollama, CPU) | Folder: `D:\Week_05` | Files: `demo.py`, `demo_2.py`, `demo_3.py`, `Prompts`, `Prompts_2`, `Prompts_3`

Lines marked **[FILL IN]** need your own input.

---

## Demo 1 - Rules vs generation (`demo.py`)

Ran 3 times; all 3 runs gave identical output.

| Input | RULE | LLM |
|---|---|---|
| A delivery van struck my parked car. | unknown | Repeated the label list ("The claim is: vehicle accident, property water damage, unknown.") |
| Water from a broken pipe damaged my kitchen. | unknown | Long made-up text about a vehicle driven "through a burst pipe" |
| My car was damaged after another driver hit it. | unknown | Rambling text that classified it as both vehicle accident and property water damage |

1. **Which inputs are missed by the rule-based classifier?** All three. They use "struck", "broken pipe" and "hit", and the rules only look for "accident", "collision", "water leak" and "burst pipe".
2. **Does the LLM always produce the same label?** In these 3 runs the output was identical (temperature 0.0). That is not a guarantee: other machines, runtime versions or settings can change the wording. It also never produced a clean label: it ignored "reply with the label only".
3. **Can the LLM produce a plausible but incorrect classification?** Yes. For the water-damage claim it wrote a fluent but invented vehicle story.
4. **Which approach is easier to test deterministically?** The rule classifier: the same input always gives the same output, so exact tests are possible.

---

## Demo 2 - Token-by-token generation (`Prompts`)

| Prompt | Output |
|---|---|
| 01 "...The capital of France is" | "The capital of France is Paris." |
| 02 "...The capital of France is not" | "The capital of France is not France itself, but rather the city of Paris, which is located in the heart of the city." |
| 03 "In a fictional world, the capital of France is" | "In a fictional world, the capital of France is Paris." |

**What changed between the prompts? Why might the continuation change?** Only a few words changed. A language model picks each next token from a probability distribution that depends on all the preceding text. Adding "not" shifted the probabilities toward negation phrases, which gave a confused sentence. "In a fictional world" did not change the answer because "capital of France, Paris" is a very strong learned pattern. The model also ignored "with one word" in all three.

---

## Demo 3 - Concise vs noisy context (`demo_2.py`, 3 trials)

| Run | Prompt A latency | Prompt B latency |
|---|---|---|
| 1 | 809.55 ms | 224.25 ms |
| 2 | 762.02 ms | 97.31 ms |
| 3 | 755.73 ms | 102.06 ms |
| **Mean** | **775.77 ms** | **141.21 ms** |

1. **Did both prompts classify the claim as vehicle?** Not cleanly. Prompt A said "Vehicle Claim" but also repeated the category list. Prompt B only repeated the claim and did not classify.
2. **Did the noisy prompt add useful information?** No, only extra wording that the model ignored.
3. **Was one prompt consistently faster?** Yes, Prompt B in all 3 runs (about 5 times faster), but only because its output was one short sentence. Output length drives latency here.
4. **Unsupported assumptions?** Yes, in Prompt A in every run: it changed "a tree fell" to "the vehicle fell on my parked car" and invented "damage to the car's body and interior".
5. **How to make the experiment more rigorous?** More claims, more trials, a fixed output limit for both prompts, automatic scoring of whether the label is correct, token counts for each prompt, a warm-up call first, and a larger model.

Note: the first version of this script had no output limit and was very slow, because a 135M model can repeat itself until the context is full. `num_predict: 100` fixed that.

---

## Demo 4 - Temperature (`demo_3.py`)

| Temp | Run 1 vs Run 2 | Format | Quality |
|---|---|---|---|
| 0 | Identical | 7 numbered sections with 3 sub-bullets each | Repetitive (sections 4 to 7 repeat) |
| 0.7 | Different | 10 numbered items in both runs | Run 1 drifted to generic machine-learning validation; Run 2 invented an unrelated "Human-Lymph Node / ELISA" topic |
| 1.0 | Different | 6 items, then 10 items | Vague and partly incoherent |

1. **Did the wording change?** At temperature 0, no. At 0.7 and 1.0, yes (structure, length and topic changed).
2. **Did all outputs obey the "exactly three bullet points" requirement?** No, none did.
3. **Did higher temperature make the response better?** No. Temperature 0 was the most consistent; higher values added randomness and hallucination, not accuracy.

---

## Demo 5 - Plausibility vs evidence (`Prompts_3`)

Model output: first paragraph said the customer has photos and has not provided a repair estimate; then the sentence "the customer has provided a fact that cannot be established" repeated about 8 times.

| Generated statement | Classification |
|---|---|
| The customer has photos of the vehicle | Supported by the input |
| They have not provided a repair estimate | Supported by the input |
| The customer has provided a fact that cannot be established | Unsupported (meaningless) |
| The customer has not provided a fact that can be established | Unsupported (contradicts the input) |
| The repeated sentences after the first paragraph | Unsupported (repetition loop) |

No statement fell into "Reasonable but not established". The model also ignored the requested 3-part list format.

**Lesson:** fluent output is not evidence. Model output is a candidate result and must be checked against the application's requirements.
