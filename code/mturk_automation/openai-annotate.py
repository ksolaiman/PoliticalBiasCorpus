import os
import csv
import time
import openai

# Make sure your API key is set:
# export OPENAI_API_KEY="sk-…"
openai.api_key = "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"

INPUT_CSV  = "../../gold/HIT_inputs/mturk_input_300.csv"
OUTPUT_CSV = "mturk_input_300_annotated.csv"

# The system prompt teaches the model your qualification task rules:
SYSTEM_PROMPT = """
You are an MTurk annotator trained on the Bias Qualification Task.
For each item, you see a title and three snippets. You are familiar with Conservative and Republican party principles.
Answer in JSON with four fields:
  Q1_score: sentiment toward Democrats (-5, -2.5, 0, +2.5, +5)
  Q2_score: sentiment toward Republicans (same scale)
  Q3_reason: a list of zero-indexed codes (strings) from:
    "0" = Author uses strong language (either positive or negative) to describe people or institutions of one side.
    "5" = Author expresses their own opinion to describe one side positively or negatively.
    "4" = Author presents principles of one political side too positively or too negatively in the news.
    "3" = One side of the story is ignored, marginalized or presented in vague terms, or exaggerated.
    "1" = Choice of sources and witnesses is one-sided (or not equal on both sides) or too general ("experts believe", "observers say").
    "2" = Author uses inaccurate/fabricated/incomplete information to support or oppose ideas or claims.
    "6" = The article didn't use any language that demonized or supported either side, and presented information impartially as just information.
    "other" = Other (provide a brief string in the “other_text” field).
  other_text: if any reason == "other", a short explanatory string; else empty.
  BiasLabel: "Left","Right", or "Center" (compare Q1 vs. Q2).
Be concise and strict.
"""

def annotate_item(title, snippet1, snippet2, snippet3):
    prompt = f"""
Title: {title}

Snippet1:
{snippet1}

Snippet2:
{snippet2}

Snippet3:
{snippet3}

Respond with JSON exactly like:
{{"Q1_score":..., "Q2_score":..., "Q3_reason":"...","BiasLabel":"..."}}
"""
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",  "content": SYSTEM_PROMPT},
            {"role": "user",    "content": prompt}
        ],
        temperature=0,
    )
    # parse the assistant’s response as JSON
    return resp.choices[0].message.content.strip()

def main():
    with open(INPUT_CSV, newline="", encoding="utf-8") as fin, \
         open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as fout:

        reader = csv.DictReader(fin)
        fieldnames = reader.fieldnames + ["Q1_score","Q2_score","Q3_reason","BiasLabel"]
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        for i, row in enumerate(reader, start=1):
            title   = row["title"]
            snippet1 = row.get("snippet1","")[:1000]  # truncate if very long
            snippet2 = row.get("snippet2","")[:1000]  # truncate if very long
            snippet3 = row.get("snippet3","")[:1000]  # truncate if very long
            try:
                out = annotate_item(title, snippet1, snippet2, snippet3)
                # convert string output into Python dict
                ann = eval(out)  
                row.update(ann)
            except Exception as e:
                print(f"Error on row {i}: {e}")
                # fill with neutral defaults on failure
                row.update({
                    "Q1_score":0, "Q2_score":0,
                    "Q3_reason":6,
                    "BiasLabel":"Center"
                })
            writer.writerow(row)

            # simple rate‐limit to avoid hitting rate caps
            time.sleep(0.5)

    print(f"Annotation complete -> {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
