from flask import Flask, render_template, request, jsonify
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import T5Tokenizer, T5ForConditionalGeneration

app = Flask(__name__)

df = pd.read_excel("SourceData.xlsx").fillna("").astype(str)
problems = df["Problem Statement / Issue / Defect"].tolist()
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")
problem_embeddings = semantic_model.encode(problems)

t5_tokenizer = T5Tokenizer.from_pretrained("Vamsi/T5_Paraphrase_Paws")
t5_model = T5ForConditionalGeneration.from_pretrained("Vamsi/T5_Paraphrase_Paws")


def clean_text(text):
    return text.replace("_x000D_", "\n").replace("\r", "").replace("\n\n", "\n").strip()


def rephrase_text(text):
    prompt = "paraphrase: " + text
    input_ids = t5_tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = t5_model.generate(input_ids, max_length=100, num_return_sequences=1, temperature=1.0)
    return t5_tokenizer.decode(outputs[0], skip_special_tokens=True)


def get_matches(user_input, threshold=0.4):
    user_embedding = semantic_model.encode([user_input])
    sims = cosine_similarity(user_embedding, problem_embeddings)[0]
    matches = [(i, s) for i, s in enumerate(sims) if s >= threshold]
    matches.sort(key=lambda x: x[1], reverse=True)

    results = []
    for idx, score in matches:
        row = df.iloc[idx]
        result = {
            "similarity": f"{score:.2f}",
            "problem": clean_text(row["Problem Statement / Issue / Defect"]),
            "solution_original": clean_text(row["Resolution Notes / Solution"]),
        }
        try:
            result["solution_rephrased"] = clean_text(rephrase_text(result["solution_original"]))
        except:
            result["solution_rephrased"] = "(Could not rephrase properly. Showing original) " + result["solution_original"]
        results.append(result)
    return results


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_question = data.get("question", "")
    results = get_matches(user_question)
    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
