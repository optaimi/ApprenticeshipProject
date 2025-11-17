# llm_explanations.py

from typing import Dict, Any
from openai import OpenAI

# Uses OPENAI_API_KEY from env
client = OpenAI()


def build_explanation_prompt(submission: Dict[str, Any], result: Dict[str, Any]) -> str:
    """
    Turn the structured validation result into a plain-English summary prompt.
    The model explains, it does NOT change any decisions.
    """
    name = submission["name"]
    category = submission["category"]
    price = submission["price"]
    age_flag = submission["age_flag"]

    overall = result["overall"]

    cat = result["category"]
    price_res = result["price"]
    age = result["age_verification"]

    prompt = f"""
You are helping a supermarket chain explain product validation results.

The rules engine has ALREADY decided everything. Your job is ONLY to explain
those decisions in clear language. Do not invent new rules, and do not change
the outcome.

Submission:
- Product name: {name}
- Store category: {category}
- Store price: £{price:.2f}
- Store age verification: {age_flag}

Validation result (from rules engine):
- Overall decision: {overall}

Category check:
- Decision: {cat['decision']}
- Message: {cat['message']}
- Predicted HO category: {cat['predicted']}
- Confidence: {cat['confidence']:.0%}

Price check:
- Decision: {price_res['decision']}
- Message: {price_res['message']}
- Typical HO median price: {price_res['median']}
- Band lower: {price_res['lower']}
- Band upper: {price_res['upper']}

Age verification check:
- Decision: {age['decision']}
- Message: {age['message']}
- Typical HO setting: {age['predicted']}
- Confidence: {age['confidence']:.0%}

Write your answer **in markdown** with this exact structure:

### For the store
- 2–4 short bullet points explaining:
  - whether the product can go through automatically, needs fixing, or will be reviewed;
  - what (if anything) the store needs to change;
  - keep it friendly and non-technical.

### For head office
- 2–4 short bullet points explaining:
  - why the engine reached this decision;
  - which parts were most important (category, price, age check);
  - anything they should double-check if there are warnings.

Use UK English. Be concise. Do not include any other headings or sections.
"""
    return prompt.strip()


def generate_explanation(submission: Dict[str, Any], result: Dict[str, Any]) -> str:
    """
    Call GPT-4.1 nano to turn the validation output into a human explanation.
    """
    prompt = build_explanation_prompt(submission, result)

    response = client.responses.create(
        model="gpt-4.1-nano",  #using as fast + cheap 
        input=[
            {
                "role": "system",
                "content": "You explain validation results clearly to supermarket staff.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        # Optional: keep it tight
        # max_output_tokens=350,
    )

    # responses API exposes a convenience property for plain text 
    return response.output_text
