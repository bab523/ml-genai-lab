import os, textwrap
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

os.makedirs("data/docs", exist_ok=True)
NOTE = "Synthetic training document for a lab exercise. Not for clinical use."

DOCS = {
"hypertension_guideline.md": ("Hypertension Management Guideline", [
 ("Diagnosis and targets", "Hypertension is diagnosed when office blood pressure is repeatedly at or above 140/90 mmHg, confirmed with home or ambulatory monitoring. For most adults the treatment target is below 130/80 mmHg. Measure blood pressure in both arms at the first visit and repeat after five minutes of seated rest."),
 ("First-line drug therapy", "First-line agents are ACE inhibitors, angiotensin receptor blockers, thiazide-like diuretics and calcium channel blockers. Most patients need two drugs to reach target. Start with a single pill combination when blood pressure is more than 20/10 mmHg above target."),
 ("Hypertensive emergency", "A blood pressure above 180/120 mmHg with signs of organ damage such as chest pain, confusion, visual loss or pulmonary oedema is a hypertensive emergency. Admit the patient and lower pressure with intravenous labetalol or nicardipine, aiming for no more than a 25 percent reduction in the first hour."),
 ("Pregnancy and special groups", "ACE inhibitors and angiotensin receptor blockers must be avoided in pregnancy because they can harm the foetus. Labetalol, nifedipine and methyldopa are preferred. In patients of African ancestry, start with a calcium channel blocker or thiazide-like diuretic."),
 ("ACE inhibitor side effects", "A dry persistent cough affects up to one in five patients on ACE inhibitors and is a reason to switch to an angiotensin receptor blocker. Check potassium and creatinine one to two weeks after starting treatment."),
]),
"diabetes_protocol.txt": ("Type 2 Diabetes Clinical Protocol", [
 ("Diagnosis and glycaemic targets", "Type 2 diabetes is diagnosed with a fasting glucose of 126 mg/dL or higher, or an HbA1c of 6.5 percent or higher. The usual HbA1c target is below 7 percent, relaxed to 8 percent in frail older adults. Classic symptoms are excessive thirst, frequent urination and unexplained weight loss."),
 ("Initial drug treatment", "Metformin is first-line therapy unless the eGFR is below 30. Start at 500 mg daily with food and increase slowly to limit gastrointestinal upset. Add an SGLT2 inhibitor or GLP-1 receptor agonist for patients with heart disease, heart failure or chronic kidney disease."),
 ("Hypoglycaemia management", "Hypoglycaemia is a blood glucose below 70 mg/dL. In a conscious patient give 15 grams of fast-acting carbohydrate such as juice or glucose tablets and recheck after 15 minutes. If the patient is unconscious give intramuscular glucagon or intravenous dextrose."),
 ("Diabetic ketoacidosis", "Suspect ketoacidosis when a patient has nausea, abdominal pain, deep rapid breathing and a fruity breath odour with high glucose and ketones. Start intravenous fluids first, then insulin infusion, and replace potassium once the level is known to be below 5.3 mmol/L."),
 ("Sick day rules", "During vomiting, diarrhoea or fever, patients should keep drinking fluids and temporarily pause metformin, SGLT2 inhibitors, ACE inhibitors and diuretics until eating normally again."),
]),
"sepsis_protocol.pdf": ("Sepsis Recognition and Management Protocol", [
 ("Recognition", "Suspect sepsis when infection is accompanied by fever or low temperature, heart rate above 90, respiratory rate above 22, altered mentation or systolic pressure below 100 mmHg. Measure serum lactate and escalate immediately to the rapid response team."),
 ("First hour bundle", "Within one hour: measure lactate, draw two sets of blood cultures before antibiotics, give broad-spectrum antibiotics, and start rapid crystalloid fluids. Delays in antibiotic administration increase mortality."),
 ("Fluid resuscitation", "Give 30 mL/kg of intravenous crystalloid for hypotension or a lactate of 4 mmol/L or more. Reassess perfusion after the bolus using capillary refill, urine output and repeat lactate."),
 ("Vasopressor support", "If mean arterial pressure remains below 65 mmHg after fluids, start norepinephrine as the first-choice vasopressor, preferably through a central line. Add vasopressin if the norepinephrine dose escalates."),
 ("Source control", "Identify and control the source of infection within 6 to 12 hours, for example by draining an abscess, relieving an obstructed urinary tract or removing an infected catheter."),
]),
"drug_interactions.pdf": ("Drug Interaction Reference", [
 ("Anticoagulant interactions", "Warfarin interacts with many drugs. NSAIDs such as ibuprofen raise bleeding risk, and antibiotics such as ciprofloxacin and trimethoprim-sulfamethoxazole increase the INR. Check the INR within three to five days of starting any new antibiotic."),
 ("Statin interactions", "Clarithromycin and erythromycin raise simvastatin levels and can cause rhabdomyolysis, which presents with muscle pain, weakness and dark urine. Withhold the statin during the antibiotic course."),
 ("Potassium and kidney interactions", "Combining ACE inhibitors with potassium-sparing diuretics such as spironolactone can cause dangerous hyperkalaemia, especially in kidney disease. Monitor potassium and creatinine regularly."),
 ("Serotonergic combinations", "Combining SSRIs with tramadol, linezolid or triptans can cause serotonin syndrome, with agitation, tremor, sweating, diarrhoea and fever. Stop the offending agents and give supportive care."),
 ("Nitrates and erectile dysfunction drugs", "Sildenafil and other PDE5 inhibitors must never be combined with nitrates such as glyceryl trinitrate because of the risk of severe hypotension."),
]),
"asthma_guideline.md": ("Asthma Management Guideline", [
 ("Stepwise treatment", "Step 1 is an as-needed short-acting beta agonist. Adults with persistent asthma should receive a low-dose inhaled corticosteroid with formoterol as reliever and controller. Step up when symptoms occur more than twice a week."),
 ("Recognising a severe exacerbation", "Signs of severe asthma include inability to speak in full sentences, respiratory rate above 25, heart rate above 110 and peak expiratory flow below 50 percent of best. Silent chest, cyanosis and exhaustion indicate life-threatening asthma."),
 ("Acute treatment", "Give oxygen to keep saturation at 93 to 95 percent, repeated nebulised salbutamol with ipratropium, and oral prednisolone 40 to 50 mg for five days. Consider intravenous magnesium sulfate for severe cases not responding."),
 ("Trigger avoidance", "Common triggers are viral infections, house dust mites, pollen, smoke and cold air. Aspirin and NSAIDs can trigger bronchospasm in some patients. Review inhaler technique at every visit."),
]),
}

def as_md(title, secs):
    out = [f"# {title}", "", NOTE, ""]
    for h, b in secs:
        out += [f"## {h}", b, ""]
    return "\n".join(out)

def as_txt(title, secs):
    out = [title, "", NOTE, ""]
    for i, (h, b) in enumerate(secs, 1):
        out += [f"{i}. {h}", b, ""]
    return "\n".join(out)

def write_pdf(path, text):
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica", 11)
    y = 800
    for line in text.split("\n"):
        for piece in (textwrap.wrap(line, 95) or [""]):
            if y < 60:
                c.showPage(); c.setFont("Helvetica", 11); y = 800
            c.drawString(50, y, piece); y -= 16
    c.save()

for name, (title, secs) in DOCS.items():
    path = f"data/docs/{name}"
    if name.endswith(".md"):
        open(path, "w").write(as_md(title, secs))
    elif name.endswith(".txt"):
        open(path, "w").write(as_txt(title, secs))
    else:
        write_pdf(path, as_txt(title, secs))
    print("created", path)
