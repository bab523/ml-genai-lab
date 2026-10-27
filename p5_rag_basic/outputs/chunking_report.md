# Chunking strategy comparison

| strategy | top1_correct_doc | top1_has_answer | top3_has_answer | avg_context_chars |
|---|---|---|---|---|
| fixed | 0.833 | 0.75 | 0.833 | 1384 |
| header | 0.917 | 0.75 | 1.0 | 788 |

## Example retrievals

### [fixed] Patient is very thirsty, urinating constantly and has lost weight
- top hit: drug_interactions.pdf (score 0.48)
- text: of severe hypotension.

### [fixed] Elderly patient on a blood thinner was just prescribed an antibiotic
- top hit: drug_interactions.pdf (score 0.44)
- text: Drug Interaction Reference Synthetic training document for a lab exercise. Not for clinical use. 1. Anticoagulant interactions Warfarin interacts with many drugs. NSAIDs such as ibuprofen raise bleeding risk, and antibiotics such as ciprofloxacin and trimethoprim-sulfamethoxazole increase the INR. C

### [header] Patient is very thirsty, urinating constantly and has lost weight
- top hit: diabetes_protocol.txt (score 0.34)
- text: Diabetic ketoacidosis Suspect ketoacidosis when a patient has nausea, abdominal pain, deep rapid breathing and a fruity breath odour with high glucose and ketones. Start intravenous fluids first, then insulin infusion, and replace potassium once the level is known to be below 5.3 mmol/L.

### [header] Elderly patient on a blood thinner was just prescribed an antibiotic
- top hit: drug_interactions.pdf (score 0.45)
- text: Statin interactions Clarithromycin and erythromycin raise simvastatin levels and can cause rhabdomyolysis, which presents with muscle pain, weakness and dark urine. Withhold the statin during the antibiotic course.
