# P9: QLoRA Fine-Tuning for Claims Processing
- Platform: free Google Colab T4 GPU (no local GPU).
- Base model: Qwen2.5-1.5B-Instruct. The handbook suggests an 8B model, but 8B often runs out of memory on a free T4, so a smaller model was used with the same technique.
- Data: 1,500 synthetic anonymized claims in chat JSONL (system, user, assistant roles); no real PII.
- Method: 4-bit NF4 quantization (bitsandbytes), LoRA r=16 on q_proj and v_proj (PEFT), trained with TRL SFTTrainer.
- Results: outputs/model_comparison.csv (base vs fine-tuned: format accuracy, decision accuracy, latency); loss curve in outputs/loss_curve.png.
- Adapter: only a few MB, compared with the multi-GB base model.
