import os
import json
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class DebertaNLI:
    def __init__(self, model_path, max_length=512):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            local_files_only=True
        )
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_path,
            local_files_only=True
        ).to(self.device)

        self.model.eval()
        self.max_length = max_length

        self.id2label = {
            int(k): v for k, v in self.model.config.id2label.items()
        }

    def predict(self, claim, evidence_sentences):
        text = " [SEP] ".join([claim.strip()] + [e.strip() for e in evidence_sentences])

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_length,
            padding=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            pred_id = torch.argmax(probs, dim=-1).item()
            confidence = probs[0][pred_id].item()

        return self.id2label[pred_id], confidence


def run_deberta_nli(query_id, claim, top_k=5):
    fusion_path = f"outputs/fusion/final_ranked_sentences_{query_id}.json"

    with open(fusion_path, "r", encoding="utf-8") as f:
        fusion_data = json.load(f)

    top_sentences = fusion_data["results"][:top_k]

    evidence_texts = [s["sentence_text"] for s in top_sentences]
    evidence_ids = [s["sentence_id"] for s in top_sentences]

    nli = DebertaNLI(model_path="Models/Model-1")
    label, confidence = nli.predict(claim, evidence_texts)

    os.makedirs("outputs/inference", exist_ok=True)
    out_path = f"outputs/inference/nli_results_{query_id}.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "query_id": query_id,
                "claim": claim,
                "label": label,
                "confidence": confidence,
                "used_sentence_ids": evidence_ids,
                "num_evidence_used": len(evidence_texts)
            },
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"🧠 DeBERTa NLI result saved to: {out_path}")
