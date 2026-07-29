# Spec-Driven Development (SDD): Scaling AI-Assisted "Vibe Coding"
**Presenter:** [Your Name]
**Audience:** Erik, Senior Director of Engineering

---

## Slide 1: Title Slide
**Title:** Scaling AI-Assisted "Vibe Coding" with Spec-Driven Development (SDD)
**Subtitle:** A framework for shipping production-grade software with LLMs
**Speaker:** [Your Name]

---

## Slide 2: The "Vibe Coding" Reality
**Title: The Promise & Pitfalls of AI Coding**
*   **The Promise ("Vibe Coding"):** Engineers using AI to go from idea to code at unprecedented speeds by describing what they want.
*   **The Problem:** Unconstrained AI coding leads to:
    *   **"Spaghetti by AI":** Inconsistent architectures and scattered business logic.
    *   **Hallucinations:** AI assuming incorrect requirements or hallucinating libraries.
    *   **The Context Window Wall:** As the codebase grows, AI loses track of the big picture.
*   **The Result:** Rapid prototyping, but a massive refactoring tax for production.

---

## Slide 3: The Solution: Spec-Driven Development (SDD)
**Title: What is SDD?**
*   **Concept:** A methodology that forces AI to think before it writes code, utilizing a structured, multi-step pipeline.
*   **How it Works:** We shift the AI's focus from "write me the code" to "help me define, clarify, and plan the architecture, *then* write the code."
*   **The Workflow (Our Pipeline):**
    1.  **Constitution:** Establishing the unbendable architectural rules.
    2.  **Specify:** Generating the high-level feature spec.
    3.  **Clarify:** AI interrogating the engineer on edge cases (e.g., GDPR, concurrent updates).
    4.  **Plan:** Formulating the implementation steps.
    5.  **Analyze & Implement:** Executing the plan with tight guardrails.

---

## Slide 4: Real-World Success: The User Management API
**Title: Proof of Concept: Multi-Tenant User API**
*   **Project:** A complex, production-grade API for multi-tenant user management.
*   **Tech Stack:** Python 3.11, FastAPI, Supabase (PostgreSQL, Auth), Edge Functions (Deno).
*   **How SDD Made the Difference:**
    *   *Without SDD:* AI would have stumbled on complex state management.
    *   *With SDD:* The AI autonomously identified and prompted us to solve critical edge cases *before* writing code:
        *   Handling concurrent role updates via JWT refreshes.
        *   GDPR hard deletion (anonymized stubs vs. row deletion).
        *   Enforcing MFA (AAL2) via Supabase Row Level Security (RLS).
        *   Distributed tracing strategies (X-Trace-Id).

---

## Slide 5: Why Use Opencode for SDD?
**Title: The Opencode Advantage**
*   **Deep Workspace Context:** Opencode operates directly in our terminal and file system, giving the AI true situational awareness.
*   **Iterative Execution:** It doesn't just write code; it runs shell commands, verifies syntax (`ruff`, `pytest`), and iterates autonomously.
*   **Agentic Workflows:** We use Opencode to seamlessly pass the output of one SDD prompt (e.g., *04 spec clarify*) into the next (*05 spec analyze*), creating an automated software factory.

---

## Slide 6: ROI & Organizational Impact
**Title: Why We Need to Scale This Now**
*   **Higher Code Quality (Day 1):** Bugs are caught in the "Clarify" phase, not in QA or Production.
*   **Architectural Consistency:** The "Constitution" ensures junior devs and AI alike adhere to Senior-level architectural standards.
*   **Faster Time-to-Market:** Retains the speed of "Vibe Coding" but eliminates the technical debt penalty.
*   **Living Documentation:** The by-product of SDD is highly detailed, up-to-date markdown specifications and architectural decision records (ADRs).

---

## Slide 7: The Ask / Next Steps
**Title: Proposed Next Steps**
*   **The Goal:** Empower our organization to code faster without sacrificing quality.
*   **Proposal:**
    1.  Host a 45-minute "Vibe Coding with SDD" workshop/demo for the engineering leads.
    2.  Identify a low-risk pilot project for another team to adopt the SDD + Opencode workflow.
    3.  Refine our internal "Prompt Library" (Constitution, Clarify, Plan) into standard company tooling.
*   **Call to Action:** "Erik, I'd love your sponsorship to demo this workflow to the wider engineering leadership next week."
