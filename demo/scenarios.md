# Demo scenarios — Depop voice support agent

Three scenarios designed to demonstrate the full range of the agent's decision logic:
clean resolution, escalation, and clarifying question before decision.

---

## Scenario 1 — clean resolution

**Category triggered:** `shipping_dispute`
**Expected outcome:** Resolves without escalation
**Decision path:** Classify → knowledge base lookup → resolution steps → ElevenLabs response

**User input (spoken or typed):**
> "I ordered a pair of jeans five days ago and the seller still hasn't shipped them.
> There's no tracking number on my order. What should I do?"

**Expected agent reasoning (visible in UI):**
```
Identifying issue type... shipping dispute detected
Checking policy... 5-day shipping threshold reached
Escalation check... no escalation triggers met
Decision: resolving directly
Generating response...
```

**Expected agent response (spoken via ElevenLabs):**
"Since it's been five days since your order and there's still no tracking,
you're now eligible to raise an issue directly in the Depop app.
Go to your order, tap 'Resolve' and select 'Item not shipped' as the reason.
The seller will have 48 hours to respond with proof of shipping.
If they don't respond, Depop will automatically refund you.
In the meantime, it's worth sending the seller a quick message first —
sometimes orders get delayed without a notification."

---

## Scenario 2 — escalation

**Category triggered:** `authenticity_claim`
**Expected outcome:** Escalates to human support — always escalates flag triggered
**Decision path:** Classify → knowledge base lookup → escalation trigger met → handoff with guidance

**User input (spoken or typed):**
> "I just received a Supreme hoodie I bought and I'm pretty sure it's fake.
> The stitching is completely wrong and the tags look nothing like the real thing.
> The seller is insisting it's authentic but I don't believe them."

**Expected agent reasoning (visible in UI):**
```
Identifying issue type... authenticity claim detected
Checking policy... always_escalates: true
Decision: escalating to human support
Preparing handoff summary...
```

**Expected agent response (spoken via ElevenLabs):**
"Authenticity disputes need to be reviewed by Depop's support team directly —
this isn't something I can resolve on your behalf, and it's important
your case is handled carefully.
Here's what to do right now: don't return the item to the seller.
Open a dispute in the Depop app within 30 days of your purchase,
and when you do, include clear photos of the stitching, labels, and any hardware
that looks wrong — the more detail the better.
Depop's team will review the evidence from both sides and make a decision.
I'll flag this as a priority escalation so you get to the right person quickly."

---

## Scenario 3 — clarifying question before decision

**Category triggered:** `item_not_as_described` (ambiguous perspective)
**Expected outcome:** Agent asks one clarifying question, then resolves on seller side
**Decision path:** Classify → ambiguous perspective detected → clarifying question →
user confirms seller → knowledge base lookup (seller view) → resolution steps

**User input (spoken or typed):**
> "My buyer is saying the jacket I sent isn't as described,
> but I listed everything accurately and sent exactly what was in the photos.
> I don't know what to do."

**Expected agent reasoning (visible in UI):**
```
Identifying issue type... item not as described detected
Checking perspective... buyer or seller unclear
Decision: clarifying question required before proceeding
```

**Expected agent response — clarifying question (spoken via ElevenLabs):**
"Before I help you with next steps, I just want to confirm —
are you the seller who sent the item, or the buyer who received it?"

**User follow-up input:**
> "I'm the seller."

**Expected agent reasoning (visible in UI):**
```
Perspective confirmed... seller
Retrieving seller-side resolution steps...
Escalation check... no always_escalates flag
Decision: resolving with seller guidance
```

**Expected agent response — resolution (spoken via ElevenLabs):**
"Got it. As the seller, the first thing to do is ask your buyer to raise
a formal issue through Depop's Resolution Centre in the app —
that way everything is documented and Depop can step in if needed.
While they do that, pull together any evidence you have that the item
matched the listing: your original photos, any messages where the condition
was discussed, and proof of postage.
If the buyer raises the issue and you provide that evidence,
Depop will review both sides before making any decision.
You won't automatically be held responsible just because a dispute was opened."