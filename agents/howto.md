# How to Use Multiple Agents

This guide explains how to effectively use multiple agents together in Cursor, Gemini Code, or other AI-powered IDEs to maximize the power of the agent system.

## How to Use Multiple Agents

### Method 1: Sequential Agent Switching (Most Common)

Switch agents as you move through different phases:

```
1. Start with `strategy/market-researcher` → Validate idea
2. Switch to `engineering/rapid-prototyper` → Set up stack
3. Switch to `engineering/backend-architect` → Design schema
4. Switch to `engineering/frontend-developer` → Build UI
5. Switch to `security/security-architect` → Security review
6. Switch to `testing/e2e-tester` → Add tests
```

**In Cursor:**

- Use `@` to reference files: `@.instructions/agents/engineering/frontend-developer.md`
- Or copy relevant sections into your chat context

### Method 2: Multi-Agent Context Loading (Powerful)

Load multiple agents simultaneously for complex tasks:

**Example: Building a Feature End-to-End**

```
@.instructions/agents/engineering/fullstack-developer.md
@.instructions/agents/security/authentication-specialist.md
@.instructions/agents/data/database-engineer.md
@.instructions/agents/testing/e2e-tester.md

"Build a user invitation feature that:
- Allows admins to invite team members
- Sends email invitations
- Handles OAuth SSO
- Includes proper RBAC
- Has E2E tests"
```

The AI will use patterns from all four agents.

### Method 3: Agent Composition Patterns

Create workflows that combine agents:

**Example: Launch Workflow**

```markdown
# Launch Workflow - Load These Agents Together

@marketing/launch-coordinator.md
@marketing/content-creator.md
@marketing/seo-specialist.md
@marketing/email-marketer.md
@project-management/project-shipper.md

"Plan and execute a Product Hunt launch for [product]"
```

**Example: Security Audit Workflow**

```markdown
@security/security-architect.md
@security/penetration-tester.md
@security/authentication-specialist.md
@testing/security-tester.md

"Conduct a security audit of our authentication system"
```

### Method 4: Create a "Super Agent" Prompt

Create a meta-prompt that orchestrates multiple agents:

```markdown
# Multi-Agent Orchestrator

You are coordinating multiple specialized agents:

**Current Context:**

- Engineering: @engineering/fullstack-developer.md
- Security: @security/authentication-specialist.md
- Testing: @testing/e2e-tester.md

**Task:** Build a secure user management feature

**Process:**

1. Use engineering agent for implementation patterns
2. Use security agent for auth/authorization checks
3. Use testing agent for test structure

**Output:** Complete feature with security and tests
```

## Practical Workflow Examples

### Example 1: Building a New Feature

**Step 1: Planning Phase**

```
@product/sprint-prioritizer.md
@strategy/competitive-intelligence.md

"Should we build [feature]? Analyze competitor solutions and prioritize."
```

**Step 2: Design Phase**

```
@design/ui-designer.md
@design/accessibility-specialist.md
@design/design-system-architect.md

"Design the UI for [feature] using our design system, ensuring accessibility."
```

**Step 3: Implementation Phase**

```
@engineering/fullstack-developer.md
@engineering/api-developer.md
@data/database-engineer.md

"Implement [feature] with proper API design and database schema."
```

**Step 4: Security & Testing Phase**

```
@security/security-architect.md
@testing/e2e-tester.md
@testing/security-tester.md

"Add security controls and comprehensive tests for [feature]."
```

**Step 5: Launch Phase**

```
@project-management/project-shipper.md
@marketing/launch-coordinator.md
@documentation/technical-writer.md

"Plan launch and create documentation for [feature]."
```

### Example 2: Using Cursor's Composer Mode

In Cursor's Composer (multi-file editing), you can:

1. **Open multiple agent files** in tabs
2. **Reference them in your prompt:**

   ```
   Using patterns from:
   - @engineering/fullstack-developer.md (for component structure)
   - @design/design-system-architect.md (for styling)
   - @testing/e2e-tester.md (for test patterns)

   Build a project management dashboard component
   ```

3. **Cursor will use all referenced contexts**

### Example 3: Creating Agent "Recipes"

Create reusable agent combinations:

**`recipes/secure-feature-development.md`:**

```markdown
# Secure Feature Development Recipe

Load these agents together:

- @engineering/fullstack-developer.md
- @security/security-architect.md
- @security/authentication-specialist.md
- @testing/security-tester.md

Use this workflow:

1. Design with security in mind
2. Implement with auth checks
3. Test security scenarios
4. Review for vulnerabilities
```

**`recipes/launch-sequence.md`:**

```markdown
# Launch Sequence Recipe

Phase 1: Content (@marketing/content-creator.md, @marketing/seo-specialist.md)
Phase 2: Coordination (@marketing/launch-coordinator.md, @project-management/project-shipper.md)
Phase 3: Communication (@marketing/email-marketer.md, @marketing/twitter-engager.md)
```

## Advanced Techniques

### 1. Agent Chaining with Context Passing

```
Step 1: @strategy/pricing-strategist.md
"Design pricing for [product]"

Step 2: @engineering/fullstack-developer.md
"Implement the pricing page using the pricing structure from step 1"

Step 3: @marketing/content-creator.md
"Write copy for the pricing page based on the implementation"
```

### 2. Parallel Agent Consultation

For complex decisions, consult multiple agents:

```
@strategy/competitive-intelligence.md
@strategy/pricing-strategist.md
@strategy/market-researcher.md

"Should we launch with freemium or paid-only?
Get perspectives from all three agents."
```

### 3. Agent Validation Loops

Use one agent to validate another's output:

```
Step 1: @engineering/backend-architect.md
"Design API for user management"

Step 2: @security/security-architect.md
"Review this API design for security issues: [paste design]"

Step 3: @testing/api-tester.md
"Create tests for this API: [paste design]"
```

## Cursor-Specific Tips

### Using Cursor Rules

Create `.cursorrules` file:

```markdown
# Cursor Rules for SaaS Development

When working on features, reference these agent patterns:

- Frontend: .instructions/agents/engineering/frontend-developer.md
- Backend: .instructions/agents/engineering/backend-architect.md
- Security: .instructions/agents/security/security-architect.md
- Testing: .instructions/agents/testing/e2e-tester.md

Always consider:

- Multi-tenancy patterns
- Security best practices
- SaaS metrics tracking
- User experience
```

### Using Cursor Chat with File References

```
@.instructions/agents/engineering/fullstack-developer.md
@.instructions/agents/design/design-system-architect.md

"Build a data table component following both agents' patterns"
```

### Using Cursor Composer

1. Open relevant agent files
2. Reference them: `Using patterns from the open agent files...`
3. Cursor uses all open context

## Best Practices

1. **Start broad, then narrow**: Load multiple agents for planning, then focus on one for implementation
2. **Keep related agents together**: Security + Testing, Design + Frontend, etc.
3. **Create agent "playbooks"**: Document which agents work well together
4. **Use agents as checklists**: Load an agent to ensure you're following best practices
5. **Don't overload**: 3-4 agents max at once, or the context gets diluted

## Quick Reference: Common Agent Combinations

| Task               | Agent Combination                                                       |
| ------------------ | ----------------------------------------------------------------------- |
| **New Feature**    | Fullstack + Security + Testing                                          |
| **API Design**     | API Developer + Security Architect + API Tester                         |
| **UI Component**   | Frontend Developer + Design System Architect + Accessibility Specialist |
| **Launch**         | Launch Coordinator + Content Creator + Email Marketer                   |
| **Security Audit** | Security Architect + Penetration Tester + Security Tester               |
| **Data Feature**   | Database Engineer + Data Pipeline Engineer + Data Analyst               |
| **Pricing Change** | Pricing Strategist + Business Model Analyst + Customer Success Manager  |

## Key Takeaway

Think of agents as specialized consultants you can bring into your conversation as needed. You can:

- **Use them one at a time** - Switch agents as you move through different phases
- **Combine them** - Load multiple agents for complex tasks that span domains
- **Chain them** - Use one agent's output as input for another
- **Create workflows** - Build reusable recipes for common tasks

The power comes from knowing when to use which agents and how to combine them effectively for your specific needs.
