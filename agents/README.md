# SaaS Agent System

A comprehensive collection of specialized AI agent personas designed for rapid SaaS development. Each agent provides detailed, actionable guidance including code patterns, tool recommendations, workflows, and best practices.

## What This Is

This is a library of AI agent "personalities" you can use in Cursor or other AI-powered IDEs. Each agent is a markdown file containing:

- **Role definition** - What the agent specializes in
- **SaaS-specific patterns** - Reusable architectures and code
- **Tool recommendations** - Specific tools for each domain
- **Rapid workflows** - Step-by-step processes
- **Code examples** - Production-ready snippets
- **Best practices** - What works in real SaaS products
- **Pitfalls to avoid** - Common mistakes

## Quick Start

1. Open the agent file for your current task
2. Copy the content or reference it in your conversation
3. Use it as context for AI-assisted development
4. Switch agents as you move between tasks

## The SaaS Stack This System Assumes

```
Frontend:     Next.js 14+ (App Router) + Tailwind + shadcn/ui
Auth:         Clerk or Supabase Auth
Database:     Supabase (Postgres) or PlanetScale
Payments:     Stripe
Email:        Resend
Hosting:      Vercel
Analytics:    Mixpanel, PostHog, or Vercel Analytics
```

## Agents by Department

### Engineering (Build the Product)

| Agent | Use When |
|-------|----------|
| [frontend-developer](engineering/frontend-developer.md) | Building dashboards, data tables, forms, auth flows |
| [backend-architect](engineering/backend-architect.md) | Designing APIs, database schemas, multi-tenancy |
| [fullstack-developer](engineering/fullstack-developer.md) | Building complete features end-to-end |
| [api-developer](engineering/api-developer.md) | Designing REST/GraphQL APIs, versioning, rate limiting |
| [integration-engineer](engineering/integration-engineer.md) | OAuth, webhooks, third-party integrations, Zapier |
| [mobile-app-builder](engineering/mobile-app-builder.md) | Building React Native/Flutter apps, in-app purchases |
| [ai-engineer](engineering/ai-engineer.md) | Adding LLM features, RAG, chatbots, AI search |
| [devops-automator](engineering/devops-automator.md) | CI/CD, deployment, monitoring, infrastructure |
| [rapid-prototyper](engineering/rapid-prototyper.md) | MVPs, weekend projects, quick validation |

### Security (Protect the Product)

| Agent | Use When |
|-------|----------|
| [security-architect](security/security-architect.md) | Security architecture, threat modeling, OWASP |
| [penetration-tester](security/penetration-tester.md) | Vulnerability testing, attack surface analysis |
| [authentication-specialist](security/authentication-specialist.md) | OAuth, SSO, MFA, session management |
| [incident-responder](security/incident-responder.md) | Security incidents, breach response, forensics |

### Data (Manage the Data)

| Agent | Use When |
|-------|----------|
| [database-engineer](data/database-engineer.md) | Schema design, query optimization, migrations |
| [data-pipeline-engineer](data/data-pipeline-engineer.md) | ETL, event streaming, data warehousing |
| [data-analyst](data/data-analyst.md) | SQL, dashboards, cohort analysis, SaaS metrics |

### Strategy (Plan the Business)

| Agent | Use When |
|-------|----------|
| [competitive-intelligence](strategy/competitive-intelligence.md) | Competitor analysis, positioning, market landscape |
| [pricing-strategist](strategy/pricing-strategist.md) | Pricing models, packaging, monetization |
| [market-researcher](strategy/market-researcher.md) | TAM/SAM/SOM, market sizing, opportunity analysis |
| [business-model-analyst](strategy/business-model-analyst.md) | Unit economics, LTV/CAC, financial modeling |

### Customer Success (Keep the Users)

| Agent | Use When |
|-------|----------|
| [onboarding-specialist](customer-success/onboarding-specialist.md) | Activation flows, time-to-value, user adoption |
| [churn-analyst](customer-success/churn-analyst.md) | Churn prediction, retention, health scoring |
| [customer-success-manager](customer-success/customer-success-manager.md) | Renewals, expansion, customer playbooks |

### Product (Decide What to Build)

| Agent | Use When |
|-------|----------|
| [trend-researcher](product/trend-researcher.md) | Market research, competitor analysis, validation |
| [feedback-synthesizer](product/feedback-synthesizer.md) | Analyzing user feedback, support tickets, reviews |
| [sprint-prioritizer](product/sprint-prioritizer.md) | Prioritizing features, planning sprints, roadmaps |

### Design (Make it Beautiful & Usable)

| Agent | Use When |
|-------|----------|
| [ui-designer](design/ui-designer.md) | Dashboard layouts, component systems, design tokens |
| [ux-researcher](design/ux-researcher.md) | User interviews, usability testing, personas |
| [brand-guardian](design/brand-guardian.md) | Brand guidelines, voice & tone, visual identity |
| [visual-storyteller](design/visual-storyteller.md) | Product demos, presentations, data visualization |
| [whimsy-injector](design/whimsy-injector.md) | Micro-interactions, celebrations, empty states |
| [accessibility-specialist](design/accessibility-specialist.md) | WCAG compliance, screen readers, inclusive design |
| [design-system-architect](design/design-system-architect.md) | Component libraries, design tokens, documentation |

### Marketing (Get Users)

| Agent | Use When |
|-------|----------|
| [tiktok-strategist](marketing/tiktok-strategist.md) | TikTok content, hooks, trend participation |
| [instagram-curator](marketing/instagram-curator.md) | Instagram posts, carousels, Reels, Stories |
| [twitter-engager](marketing/twitter-engager.md) | Twitter threads, building in public, engagement |
| [reddit-community-builder](marketing/reddit-community-builder.md) | Reddit engagement, community building |
| [app-store-optimizer](marketing/app-store-optimizer.md) | ASO, keywords, screenshots, app store listings |
| [content-creator](marketing/content-creator.md) | Blog posts, SEO content, landing page copy |
| [growth-hacker](marketing/growth-hacker.md) | Growth experiments, viral mechanics, PLG |
| [seo-specialist](marketing/seo-specialist.md) | Technical SEO, programmatic pages, content optimization |
| [email-marketer](marketing/email-marketer.md) | Email sequences, automation, deliverability |
| [launch-coordinator](marketing/launch-coordinator.md) | Product Hunt, beta launches, go-to-market |

### Documentation (Explain the Product)

| Agent | Use When |
|-------|----------|
| [technical-writer](documentation/technical-writer.md) | API docs, integration guides, tutorials |
| [knowledge-base-curator](documentation/knowledge-base-curator.md) | Help center, FAQs, troubleshooting guides |

### Project Management (Ship It)

| Agent | Use When |
|-------|----------|
| [experiment-tracker](project-management/experiment-tracker.md) | A/B tests, experiment design, statistical analysis |
| [project-shipper](project-management/project-shipper.md) | Launch planning, feature flags, rollout strategies |
| [studio-producer](project-management/studio-producer.md) | Content production, creative workflows |

### Studio Operations (Keep it Running)

| Agent | Use When |
|-------|----------|
| [support-responder](studio-operations/support-responder.md) | Support tickets, help docs, customer communication |
| [analytics-reporter](studio-operations/analytics-reporter.md) | MRR tracking, dashboards, SaaS metrics |
| [infrastructure-maintainer](studio-operations/infrastructure-maintainer.md) | Monitoring, incidents, cost optimization |
| [legal-compliance-checker](studio-operations/legal-compliance-checker.md) | GDPR, privacy policies, terms of service |
| [finance-tracker](studio-operations/finance-tracker.md) | Unit economics, financial reports, forecasting |

### Testing (Make it Work)

| Agent | Use When |
|-------|----------|
| [tool-evaluator](testing/tool-evaluator.md) | Evaluating auth, database, payment tools |
| [api-tester](testing/api-tester.md) | API testing, webhook testing, integration tests |
| [workflow-optimizer](testing/workflow-optimizer.md) | CI/CD optimization, development workflows |
| [performance-benchmarker](testing/performance-benchmarker.md) | Load testing, web vitals, database performance |
| [test-results-analyzer](testing/test-results-analyzer.md) | Test analysis, flaky tests, quality metrics |
| [security-tester](testing/security-tester.md) | Security scanning, SAST/DAST, vulnerability detection |
| [e2e-tester](testing/e2e-tester.md) | Playwright/Cypress, user flow testing, visual regression |

## Common Workflows

### Building an MVP (Weekend Project)

1. Start with `rapid-prototyper` - Get the stack and shortcuts
2. Use `backend-architect` - Design minimal schema
3. Use `frontend-developer` - Build the dashboard
4. Use `devops-automator` - Deploy to Vercel

### Adding a New Feature

1. Use `sprint-prioritizer` - Decide if it's worth building
2. Use `frontend-developer` or `backend-architect` - Build it
3. Use `project-shipper` - Plan the rollout
4. Use `experiment-tracker` - Measure impact

### Building Secure SaaS

1. Use `security-architect` - Design security architecture
2. Use `authentication-specialist` - Implement auth properly
3. Use `security-tester` - Add automated security scans
4. Use `penetration-tester` - Validate before launch

### Setting Up Analytics & Data

1. Use `data-analyst` - Define key metrics
2. Use `database-engineer` - Optimize queries
3. Use `data-pipeline-engineer` - Set up event tracking
4. Use `analytics-reporter` - Build dashboards

### Launching a Product

1. Use `content-creator` - Write landing page
2. Use `seo-specialist` - Optimize for search
3. Use `launch-coordinator` - Plan Product Hunt launch
4. Use `email-marketer` - Set up sequences
5. Use `twitter-engager` / `reddit-community-builder` - Announce

### Handling Growth

1. Use `analytics-reporter` - Track metrics
2. Use `feedback-synthesizer` - Understand users
3. Use `churn-analyst` - Identify at-risk customers
4. Use `customer-success-manager` - Improve retention
5. Use `infrastructure-maintainer` - Scale infrastructure
6. Use `performance-benchmarker` - Optimize bottlenecks

### Expanding to Enterprise

1. Use `security-architect` - SOC 2 preparation
2. Use `authentication-specialist` - Add SSO/SAML
3. Use `pricing-strategist` - Design enterprise pricing
4. Use `legal-compliance-checker` - Review compliance

## Agent File Structure

Each agent follows this structure:

```markdown
# [Agent Name]

## Role
What this agent specializes in

## Context
When to use this agent

## Core Responsibilities
Key tasks this agent handles

## [Domain-Specific Patterns]
Detailed patterns, architectures, code examples

## Tool Recommendations
Specific tools for this domain

## Rapid Development Workflows
Step-by-step processes

## Best Practices
What works

## Pitfalls to Avoid
Common mistakes

## Output Format
What the agent produces
```

## Creating Custom Agents

Use [TEMPLATE.md](TEMPLATE.md) as a starting point:

1. Copy the template
2. Define the role and context
3. Add domain-specific patterns
4. Include code examples
5. List recommended tools
6. Document workflows and best practices

## Tips for Best Results

1. **Be specific** - Tell the AI which agent context you want to use
2. **Combine agents** - Some tasks benefit from multiple perspectives
3. **Reference code patterns** - The examples are production-ready
4. **Follow the workflows** - They're optimized for speed
5. **Check tool recommendations** - They're curated for SaaS

## Philosophy

These agents are designed for:

- **Speed** - Ship in days, not months
- **Pragmatism** - Use proven tools and patterns
- **Quality** - Production-ready code and practices
- **Learning** - Understand why, not just how

They're not designed for:

- Over-engineering
- Theoretical perfection
- Enterprise complexity (unless needed)
- Analysis paralysis
