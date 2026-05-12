# AI Governance Control Tower

**Document version:** 0.1  
**Date:** 2026-05-12  
**Project mode:** Local-first MVP, Azure-aware architecture  

> This project is a prototype governance layer for registering, monitoring, evaluating, reviewing, and auditing AI systems. It is not a legal compliance product and should not be marketed as guaranteeing compliance with any law, standard, or certification.


## Design objective

The dashboard should feel secure, trustworthy, operational, and insightful.

It should not look like a generic SaaS admin panel. It should feel like an AI governance command centre: serious, calm, dense enough for monitoring, but not chaotic.

Design north star:

> A bank, healthcare organisation, regulator, or security team should be able to look at this interface and feel that the product understands oversight, risk, evidence, and control.

## Personality

| Attribute | Direction |
|---|---|
| Secure | Deep navy surfaces, restrained contrast, strong hierarchy, no playful gradients. |
| Trusting | Calm spacing, clear status labels, stable typography, transparent evidence. |
| Insightful | Risk heatmaps, timelines, posture scores, relationships, not just KPI cards. |
| Operational | Command-centre layout, live signals, review queues, incidents, audit trails. |
| Accountable | Every decision has owner, reason, timestamp, and evidence. |

Avoid:

- Generic white SaaS dashboard.
- Crypto/gaming neon overload.
- Excessive glassmorphism.
- Vague AI sparkle imagery.
- Hype copy like “autonomous compliance”.
- Colour-only risk communication.

## Visual reference language

Inspiration should come from:

- Security operations centres.
- Risk terminals.
- Air traffic control and mission control.
- Financial monitoring platforms.
- Observability platforms.
- Enterprise cloud security dashboards.

Do not copy these products, but borrow the feeling of controlled complexity.

## Colour palette

### Core surfaces

| Token | Hex | Use |
|---|---:|---|
| `--ink-950` | `#020617` | App background, deepest areas. |
| `--midnight-925` | `#06111F` | Main gradient base. |
| `--navy-900` | `#081827` | Sidebar and header surfaces. |
| `--panel-875` | `#0B1F33` | Primary cards/panels. |
| `--panel-825` | `#10263D` | Elevated panels/drawers. |
| `--panel-750` | `#17324F` | Active states and subtle highlights. |
| `--line-700` | `#24364D` | Borders/dividers. |
| `--line-600` | `#2F4663` | Focused borders. |

### Text

| Token | Hex | Use |
|---|---:|---|
| `--text-primary` | `#E6EEF8` | Main text. |
| `--text-secondary` | `#A8B8CA` | Supporting text. |
| `--text-muted` | `#718198` | Metadata and labels. |
| `--text-disabled` | `#4D5E73` | Disabled content. |
| `--text-inverse` | `#04111F` | Text on bright accents. |

### Semantic accents

| Token | Hex | Meaning |
|---|---:|---|
| `--trust-teal` | `#20D6B5` | Trusted, secure, healthy, verified. |
| `--signal-cyan` | `#38BDF8` | Live activity, links, discovery, neutral signal. |
| `--insight-violet` | `#8B5CF6` | Analysis, evaluations, model intelligence. |
| `--approved-green` | `#22C55E` | Approved/pass/success. |
| `--warning-amber` | `#F59E0B` | Medium risk, needs review, caution. |
| `--risk-orange` | `#F97316` | Elevated risk. |
| `--critical-red` | `#EF4444` | High risk, failure, incident. |
| `--blocked-rose` | `#F43F5E` | Blocked, rejected, policy violation. |
| `--unknown-slate` | `#64748B` | Unknown, unclassified, no data. |

### Risk scale

| Risk | Background | Border | Text |
|---|---:|---:|---:|
| Low | `rgba(34, 197, 94, 0.14)` | `rgba(34, 197, 94, 0.45)` | `#86EFAC` |
| Medium | `rgba(245, 158, 11, 0.15)` | `rgba(245, 158, 11, 0.50)` | `#FCD34D` |
| High | `rgba(249, 115, 22, 0.16)` | `rgba(249, 115, 22, 0.55)` | `#FDBA74` |
| Critical | `rgba(239, 68, 68, 0.18)` | `rgba(239, 68, 68, 0.60)` | `#FCA5A5` |
| Unknown | `rgba(100, 116, 139, 0.16)` | `rgba(100, 116, 139, 0.45)` | `#CBD5E1` |

### Background gradients

Use subtle gradients, not decorative gradients.

```css
--bg-app: radial-gradient(circle at top left, rgba(32, 214, 181, 0.08), transparent 28%),
          radial-gradient(circle at bottom right, rgba(139, 92, 246, 0.08), transparent 32%),
          linear-gradient(135deg, #020617 0%, #06111F 45%, #081827 100%);

--panel-gradient: linear-gradient(180deg, rgba(16, 38, 61, 0.92) 0%, rgba(11, 31, 51, 0.94) 100%);

--risk-glow: 0 0 0 1px rgba(239, 68, 68, 0.25), 0 0 28px rgba(239, 68, 68, 0.14);

--trust-glow: 0 0 0 1px rgba(32, 214, 181, 0.28), 0 0 28px rgba(32, 214, 181, 0.12);
```

## Tailwind token sketch

```ts
// frontend/tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        ink: { 950: '#020617' },
        midnight: { 925: '#06111F' },
        navy: { 900: '#081827' },
        panel: {
          875: '#0B1F33',
          825: '#10263D',
          750: '#17324F',
        },
        line: {
          700: '#24364D',
          600: '#2F4663',
        },
        trust: { teal: '#20D6B5' },
        signal: { cyan: '#38BDF8' },
        insight: { violet: '#8B5CF6' },
        risk: {
          low: '#22C55E',
          medium: '#F59E0B',
          high: '#F97316',
          critical: '#EF4444',
          blocked: '#F43F5E',
          unknown: '#64748B',
        },
      },
      boxShadow: {
        panel: '0 18px 60px rgba(0, 0, 0, 0.28)',
        trust: '0 0 28px rgba(32, 214, 181, 0.14)',
        risk: '0 0 28px rgba(239, 68, 68, 0.14)',
      },
      borderRadius: {
        panel: '18px',
      },
    },
  },
}
```

## Typography

### Font direction

Use a modern sans with high legibility and a technical-but-not-gimmicky feel.

Recommended stack:

```css
font-family: "Geist", "Inter", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
```

Monospace for run IDs, hashes, model versions, tokens, and audit metadata:

```css
font-family: "Geist Mono", "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
```

### Text styles

| Style | Size | Weight | Line height | Use |
|---|---:|---:|---:|---|
| Display | 32–40 | 650 | 1.05 | Rare hero/posture score. |
| Page title | 24–28 | 650 | 1.15 | Page headings. |
| Panel title | 14–16 | 650 | 1.3 | Card titles. |
| Body | 14 | 400 | 1.5 | Standard content. |
| Body small | 13 | 400 | 1.45 | Metadata. |
| Label | 11–12 | 600 | 1.2 | Uppercase labels. |
| Mono data | 12–13 | 500 | 1.3 | IDs, timestamps, versions. |

Labels should use letter spacing sparingly:

```css
text-transform: uppercase;
letter-spacing: 0.04em;
```

## Layout principles

### App shell

Use a command-centre layout:

```text
┌────────────────────────────────────────────────────────────┐
│ Top context bar: org, environment, date range, user         │
├───────────────┬────────────────────────────────────────────┤
│ Secure nav    │ Main operational workspace                 │
│               │                                            │
│ Risk areas    │ Panels, maps, review queues, timelines     │
│ Review count  │                                            │
│ User role     │                                            │
└───────────────┴────────────────────────────────────────────┘
```

### Grid

Use a 12-column grid on desktop.

Recommended dashboard layout:

```text
Row 1: 5 metric cards across
Row 2: Risk posture donut | Risk heatmap | Model runs trend
Row 3: Evaluation failure | Cost by model | Recent incidents
Row 4: Human review queue | Incident table / system graph
```

On smaller screens, stack cards but keep the risk posture and review queue prominent.

### Density

This app should be denser than a marketing SaaS dashboard, but not overwhelming.

Rules:

- Use tight but readable card padding: 16–20px.
- Keep card headers compact.
- Use tables with strong row hover and readable spacing.
- Prefer tabbed details over long scrolling pages.
- Do not hide critical risk information behind too many clicks.

## Component design

### Metric card

Purpose: quick operational awareness.

Contents:

- Label.
- Main value.
- Trend indicator.
- Tiny icon.
- Optional sparkline.

Variants:

- Neutral.
- Trust/healthy.
- Warning.
- Critical.

### Risk badge

Badges must include text and colour.

Example:

```tsx
<RiskBadge level="high" />
```

Visual:

```text
[ High ]
```

Do not use a red dot alone.

### Approval status badge

Statuses:

- `Pending`
- `Approved`
- `Blocked`
- `Needs changes`
- `Retired`

Use different shape/icon from risk badges to avoid confusion.

### Risk heatmap

This is a flagship visual.

Rows:

- Departments.

Columns:

- Low, medium, high, critical.

Cell:

- Count of AI systems or events.
- Colour intensity based on count and severity.
- Tooltip showing systems.

Click-through:

- Opens filtered systems list.

### Review detail drawer/page

Must feel like an evidence review, not just a modal.

Sections:

- Run metadata.
- System context.
- Input.
- Output.
- Retrieved documents.
- Evaluation result.
- PII highlights.
- Risk score.
- Decision actions.
- Reviewer notes.

Actions:

- Approve.
- Reject.
- Escalate.
- Request prompt change.

### Incident page

Incident detail should show:

- Severity.
- Status.
- System.
- Run ID.
- Detection reason.
- Evidence snippets.
- Owner.
- Timeline.
- Linked audit events.
- Resolution notes.

### Audit log

Audit log design should prioritise trust.

Columns:

- Time.
- Actor.
- Action.
- Entity.
- Change summary.
- Source.
- Export flag.

Rows should be expandable to show before/after JSON safely.

## Data visualisation principles

### Use charts for decisions, not decoration

Each chart must answer a governance question.

| Visual | Governance question |
|---|---|
| Risk heatmap | Where is AI risk concentrated? |
| Posture score | Is governance improving or deteriorating? |
| Model runs trend | Is AI usage increasing and where? |
| Failed evaluation trend | Are controls catching more issues? |
| Cost by model | Which models are driving spend? |
| Incident timeline | What went wrong and when? |
| System graph | Which systems touch sensitive data and models? |

### Chart colour rules

- Use semantic colours consistently.
- Do not assign random colours to risk levels.
- For model/provider charts, use neutral colours unless risk is implied.
- Use muted axes and gridlines.
- Tooltips should include plain-language interpretation.

### Avoid false precision

Do not show governance posture as if it is objectively exact.

Better:

```text
Governance posture: 72 / 100
Based on registry completeness, review coverage, incident rate, policy compliance, and unresolved risk.
```

Not:

```text
AI compliance score: 98.734%
```

## Page concepts

### 1. Overview dashboard

Purpose: executive and governance-team situational awareness.

Must show:

- Total AI systems.
- Risk posture.
- Pending approvals.
- Human reviews waiting.
- PII incidents.
- Failed evaluations.
- Model usage and cost.
- Recent incidents.

### 2. AI systems registry

Purpose: see what AI systems exist and who owns them.

Design direction:

- Dense table.
- Strong filters.
- Risk and approval badges.
- Row click opens system detail.
- Prominent “Register AI System” action.

### 3. System detail page

Purpose: AI system passport.

Tabs:

- Overview.
- Runs.
- Evaluations.
- Prompts.
- Data sources.
- Reviews.
- Audit log.

Hero area:

- System name.
- Approval badge.
- Risk level.
- Owner.
- Model.
- Personal data flag.
- Human oversight flag.

### 4. Human review queue

Purpose: decision workflow.

Design direction:

- Queue on left.
- Review detail on right or full detail page.
- Risk reasons visible before output details.
- Sticky decision actions.

### 5. Incidents

Purpose: operational risk response.

Design direction:

- Incident summary cards.
- Table with severity and status.
- Detail page with timeline and linked evidence.

### 6. Cost and usage

Purpose: business accountability.

Design direction:

- Cost by system.
- Cost by model.
- Runs by department.
- Average latency.
- Token usage.

### 7. Audit logs

Purpose: evidence trail.

Design direction:

- Serious, readable, filterable.
- Export controls.
- Expandable details.
- No playful visual effects.

### 8. Settings and integrations

Purpose: show local and Azure-ready configuration.

Design direction:

- Integration cards.
- Status: Local mock, Connected, Needs config, Disabled.
- Clear cloud mapping.

## Motion and interaction

Use restrained motion:

- 120–180ms transitions.
- Subtle hover states.
- No bouncing.
- No excessive animated gradients.
- Use skeleton loading for data panels.
- Use toasts for actions, but important governance actions should also update audit/event views.

## Accessibility rules

- WCAG AA contrast as baseline.
- Do not rely on colour alone.
- Keyboard navigable tables and forms.
- Focus states must be visible.
- Charts need accessible summaries.
- Review decisions require confirmation for reject/block/escalate actions.
- Error messages should be specific and non-blaming.

## Copywriting tone

Use calm, precise language.

Good:

```text
This run requires review because personal data was detected in the output.
```

Bad:

```text
Critical AI chaos detected!
```

Good:

```text
Approved with human oversight required.
```

Bad:

```text
Compliant.
```

Avoid claiming legal compliance.

Use:

- “Governance evidence.”
- “Audit-ready export.”
- “Risk signal.”
- “Review required.”
- “Policy alignment.”

Avoid:

- “Guaranteed compliant.”
- “Regulator-proof.”
- “Fully safe.”
- “Eliminates hallucinations.”

## Final visual principle

The interface should make users feel:

> “We know what AI systems exist, what they are doing, where risk is emerging, and who is accountable for decisions.”
