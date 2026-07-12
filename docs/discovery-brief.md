# Discovery Brief: Voice Support Triage Agent for Depop
---

## Executive Summary

Depop is a peer-to-peer fashion resale marketplace with over 30 million users globally, operating primarily across the UK and US. Despite strong community engagement and brand affinity among Gen Z, the platform carries a 3.1-star rating across over 7,000 Trustpilot reviews with the overwhelming majority of complaints concentrated in a narrow set of repetitive, structured support issues that do not require human judgment to resolve.

This brief proposes a voice AI support triage agent, built on ElevenLabs' speech synthesis technology, that intercepts these high-volume, low-complexity queries before they reach Depop's human support queue resolving what it can, and escalating what it can't with a structured handoff summary.

---

## The Problem

### What the data shows

Analysis of Trustpilot reviews reveals a consistent complaint pattern concentrated in five areas:

1. **Non-delivery disputes**: sellers not shipping, tracking not updating, items lost in transit
2. **Item not as described**: wrong size, wrong colour, undisclosed damage, misrepresented condition
3. **Authenticity claims**: counterfeit designer goods, fake perfume, replica luxury items
4. **Payout delays**: sellers not receiving payment after confirmed delivery
5. **Account suspension**: unexplained bans, funds withheld, no clear escalation path

Across these categories, two failure modes appear repeatedly:

- **Slow response times**: users waiting days or weeks for a first reply, often missing policy windows (30-day dispute deadline) while waiting
- **Inconsistent resolution**: users receiving different answers for the same issue, or being given incorrect policy information

### The support gap

Depop's current support infrastructure has no live chat. Users submit tickets via email or in-app forms and wait. One reviewer noted: *"the system is not designed to handle nuance like a person"* yet the majority of complaints are not nuanced. They are the same six questions asked by different people every day.

This is the gap. Not a knowledge problem. Not a policy problem. A delivery problem.

---

## The Opportunity

### Why voice AI

Voice is the natural medium for distressed users. Someone whose package hasn't arrived or who has just opened a counterfeit item is not in the mood to fill out a form. They want to say what happened and hear what to do next.

ElevenLabs' text-to-speech technology produces responses indistinguishable from human support agents. Warm, clear, and conversational. Combined with Claude's reasoning capabilities for classification and decision-making, this enables a support experience that feels human without requiring a human to be present.

### What an agent can handle autonomously

Based on the Trustpilot complaint analysis, the following query types have clear, policy-defined resolution paths that require no human judgment:

- Non-delivery queries where the 5-day threshold has or hasn't been reached
- INAD disputes where the issue clearly meets or clearly doesn't meet Depop's coverage criteria
- Payout delays within normal processing windows
- General policy and fee queries

### What an agent should always escalate

- Authenticity claims (require evidence review)
- Account suspensions (require access to account data)
- Fraud and off-platform payment disputes (require investigation)
- Ambiguous queries crossing multiple categories

This distinction, resolve vs escalate, is the core design decision of the agent, and the one that determines its commercial value.

---

## The Commercial Case

### Cost reduction

Depop's support volume scales with transaction volume. Every new user and every new sale creates potential support load. A triage agent that resolves 40–60% of inbound queries autonomously reduces headcount requirements non-linearly as the platform grows — the cost of the agent does not scale with volume the way human agents do.

### Speed as a retention mechanism

The 30-day dispute window means slow support has a direct commercial cost: users who don't get a timely response miss their protection window, lose money, and churn. An agent that responds in seconds rather than days keeps users within their eligibility window and within the platform.

### Trust as a competitive differentiator

Depop competes with Vinted, Poshmark, and eBay for the resale market. Vinted carries a significantly higher satisfaction rating partly because it has no seller fees, but also because its dispute resolution is faster. Depop's 3.1-star Trustpilot rating is a visible liability in a market where trust is the primary purchase driver. A demonstrably better support experience is a differentiator, not just an operational improvement.

---

## Proposed Solution

A voice-first support triage agent accessible via the Depop app or web platform. Users describe their issue in natural language, by voice or text, and the agent:

1. Classifies the issue into one of eight support categories
2. Retrieves the relevant policy guidance from a structured knowledge base
3. Decides whether to resolve directly or escalate to human support
4. Responds in natural, human-sounding speech via ElevenLabs TTS
5. If escalating, provides a structured handoff summary so the human agent has full context before the conversation begins

The agent handles the repetitive 60%. Human agents handle the complex 40%, with better context and less backlog.

---

## What a Real Deployment Would Require

This proposal is currently demonstrated as a working prototype. Moving to production would require:

**Phase 1 — Integration**
- Connection to Depop's existing ticketing system (likely Zendesk) to log all agent interactions and handoffs
- Authentication layer to verify user identity before discussing order-specific details
- Knowledge base pipeline connected to Depop's live help centre content so policy updates propagate automatically

**Phase 2 — Data and safety**
- Legal review of any AI-generated support responses for liability exposure
- Moderation layer to catch hallucinations or off-policy responses before they reach users
- GDPR compliance review for voice data handling and storage

**Phase 3 — Rollout**
- Pilot with a subset of inbound query types (non-delivery only, for example) before expanding
- A/B test against current support flow to measure resolution rate, time-to-resolution, and CSAT
- Human review of all escalation summaries in early phase to validate quality

---

## The Internal Buyer

The primary stakeholder for this proposal is Depop's **Head of Customer Experience**, **VP of Operations** or whoever owns the support cost line and the CSAT metric. Secondary stakeholders are the product and engineering teams who would own the integration work.

The pitch is operational and commercial, not technical: this reduces cost, increases speed, and improves the metric that most directly affects user trust and retention.

---

*This brief was produced as part of a portfolio project demonstrating applied voice AI deployment strategy. The prototype referenced is available at: github.com/v-llnetv-ca/depop-voice-agent*