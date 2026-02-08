# Engagement-Based Model: Conceptual Foundation

**Date:** 2026-02-08
**Status:** Approved conceptual model for implementation

---

## Overview

Service-Engine-X is being refactored from a transactional order-tracking system to an engagement-based project delivery platform. This document captures the conceptual foundation for this shift.

---

## 1. The Conceptual Shift

### Current Model (Order-Centric)

The API was built to model SPP.co's transactional SaaS pattern:

- **Services** = Customer-facing products in a catalog
- **Orders** = Transactions when customers buy services (conflates financial record + work delivery)
- **Tickets** = Support requests (separate from order communication)
- **Order messages** = Communication about specific orders

This treats the business like e-commerce: catalog → purchase → support.

### New Model (Engagement-Centric)

We're a service delivery business, not transactional SaaS:

- **Engagements** = Active work relationships with clients (contains projects)
- **Projects** = Discrete deliverables with clear completion states and phases
- **Conversations** = Engagement-scoped communication (unified, not fragmented)
- **Services** = Internal capability templates (not customer-facing catalog)
- **Orders** = Financial transaction records only (not delivery tracking)
- **Proposals** = Sales documents that create engagements when signed

### Why This Matters

- A single sale often includes multiple discrete deliverables
- Work has phases and progression, not just "done/not done"
- The client relationship outlives any individual project
- Communication about "Project A" and "billing questions" shouldn't be in separate systems

---

## 2. Entity Relationships

### Hierarchy

```
Engagement (work relationship with client)
├── Project: "Website Redesign" (phase: Build)
├── Project: "SEO Audit" (phase: Handoff)
├── Project: "Content Strategy" (phase: Kickoff)
├── Conversation: "Weekly Syncs"
├── Conversation: "Technical Questions"
└── Conversation: "Scope Changes"
```

### Engagement

The container for an active work relationship.

- Stays open while you're working with the client
- A client might have multiple engagements (different service areas, different contracts)
- Has status: active, paused, closed
- Links to the order(s) that funded it

### Projects

Discrete deliverables with clear completion.

- Each has phases: **Kickoff → Setup → Build → Testing → Deployment → Handoff**
- Projects complete; engagements continue
- Multiple projects can be active simultaneously
- Created from proposal items when proposal is signed

### Conversations

All communication scoped to the engagement.

- Not fragmented by which project or which order
- About the relationship as a whole
- Replaces both `order_messages` and `tickets`
- Can have multiple conversations per engagement (different topics/threads)

---

## 3. Proposal Signing Flow

When a proposal is signed/paid, it creates **two separate entities**:

### 1. Order (Financial Transaction Record)

- Links to the invoice/payment
- Records what was purchased and when
- References the engagement it funded
- Answers: "What did they pay for?"

### 2. Engagement (Work Relationship Container)

- Contains the projects to be delivered
- Proposal items become projects
- One proposal with 3 items → 1 engagement with 3 projects
- All future communication happens in conversations here
- Answers: "What are we delivering and how's it going?"

**Key Separation:** Financial records (orders) are distinct from work containers (engagements).

---

## 4. Comparison: Order-Centric vs Engagement-Centric

| Aspect | Order-Centric (Current) | Engagement-Centric (New) |
|--------|------------------------|--------------------------|
| **Core unit** | Order (transaction + work) | Engagement (work relationship) |
| **Work tracking** | Order status (Unpaid/In Progress/Complete) | Project phases (Kickoff → Handoff) |
| **Communication** | Fragmented: order_messages + tickets | Unified: conversations on engagement |
| **Client relationship** | Implicit (collection of orders) | Explicit (the engagement itself) |
| **Multi-deliverable sales** | Multiple orders, or order_items | One engagement with multiple projects |
| **After delivery** | Order closed, start new order | Project completes, engagement continues |

### Mental Model Shift

- **Old:** "We process orders and handle support tickets"
- **New:** "We manage client engagements that contain projects and conversations"

---

## 5. Database Changes

### Tables to Add

| Table | Purpose |
|-------|---------|
| `engagements` | Work relationship containers |
| `projects` | Discrete deliverables with phases |
| `conversations` | Engagement-scoped communication threads |
| `conversation_messages` | Messages within conversations |

### Tables to Keep (Repurposed)

| Table | New Purpose |
|-------|-------------|
| `orders` | Financial transaction records only, links to engagement |
| `proposals` | Sales documents, creates engagement when signed |
| `services` | Internal capability templates (not customer catalog) |
| `invoices` | Billing, references orders/engagements |

### Tables to Deprecate

| Table | Replaced By |
|-------|-------------|
| `tickets` | `conversations` |
| `ticket_messages` | `conversation_messages` |
| `order_messages` | `conversation_messages` |

---

## 6. Project Phases

Each project progresses through defined phases:

1. **Kickoff** - Initial meeting, requirements gathering
2. **Setup** - Environment setup, access provisioning
3. **Build** - Active development/creation
4. **Testing** - QA, review cycles
5. **Deployment** - Launch, go-live
6. **Handoff** - Documentation, training, transition

Projects have discrete completion. Engagements stay open while the relationship continues.

---

## 7. Key Principles

1. **Separation of concerns:** Financial transactions ≠ work delivery
2. **Relationship-first:** The engagement is the core unit, not the order
3. **Unified communication:** One place for all client communication
4. **Phase-based progression:** Work moves through defined stages
5. **Discrete completion:** Projects complete, engagements continue
