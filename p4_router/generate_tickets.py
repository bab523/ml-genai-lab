import random
import pandas as pd

random.seed(5)
T = [
 ("billing", "high", "I was charged twice for my {plan} plan this month. Please refund the duplicate payment today."),
 ("billing", "medium", "Invoice #{n} shows the wrong amount. We agreed on {plan} pricing in our contract."),
 ("billing", "low", "How do I update the credit card on file? Our card expires next quarter."),
 ("technical", "high", "Our production integration has returned HTTP 500 errors on the /{ep} endpoint since this morning. Customers are affected."),
 ("technical", "medium", "We get a 429 rate limit error on /{ep} about once an hour. Can you check our limits?"),
 ("technical", "low", "The docs say the field is user_id but the /{ep} response returns userId. Minor, but confusing."),
 ("feature_request", "low", "It would be great to have a dark mode in the dashboard."),
 ("feature_request", "medium", "Please add SSO with Okta. Our security team requires it before we renew the {plan} plan."),
 ("feature_request", "low", "Can you add CSV export for the {ep} reports?"),
]
rows = []
for i in range(60):
    cat, pri, tpl = T[i % len(T)]
    text = tpl.format(plan=random.choice(["Basic", "Pro", "Enterprise"]),
                      n=random.randint(1000, 9999),
                      ep=random.choice(["orders", "users", "payments", "reports"]))
    rows.append({"ticket_id": i, "text": text, "true_category": cat, "true_priority": pri})
pd.DataFrame(rows).to_csv("data/tickets.csv", index=False)
print("saved", len(rows), "tickets")
