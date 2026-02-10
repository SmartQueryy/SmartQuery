
# Mobile Application Design Specification

This document outlines the design and implementation plan for adapting the Resume Optimizer SaaS product for mobile devices. The design is synthesized from the collective expertise of the UI/UX, animation, and engineering agents.

## 1. Guiding Principles

- **Mobile-First, Desktop-Adapted:** While adapting a desktop app, we will prioritize a true mobile-native feel. Components and layouts are designed for small screens first and then adapted for larger ones. (Derived from `ux-researcher`, `ui-designer`).
- **Performant & Fluid:** Animations and interactions will be lightweight, purposeful, and optimized for mobile CPUs to ensure a smooth 60fps experience. We will favor CSS transforms and opacity changes. (Derived from `animations-specialist`).
- **Consistent & On-Brand:** The mobile design will adhere to the existing design system, including colors, typography, and spacing, to maintain a consistent brand identity. (Derived from `ui-designer`).
- **Action-Oriented:** The mobile experience will focus on the most common, on-the-go user actions: checking status, viewing feedback, and quick edits. (Derived from `ux-researcher`).
- **Component-Driven:** We will reuse and adapt existing React components wherever possible, using responsive props and styles to avoid duplicating code. (Derived from `frontend-developer`).

## 2. Global Navigation

The primary desktop sidebar navigation will be replaced with a top navigation bar and a slide-out menu on mobile.

### 2.1. Top Navigation Bar

The top bar provides access to the main navigation, user profile, and primary actions.

**ASCII Wireframe:**
```
┌──────────────────────────────────────────────────┐
│ [☰]  Resume Optimizer      [🔔]  [👤]             │
└──────────────────────────────────────────────────┘
```

- **`[☰]` (Hamburger Menu):** Toggles the slide-out navigation menu.
- **`Resume Optimizer` (Logo/Title):** Centered or to the right of the menu icon.
- **`[🔔]` (Notifications):** Opens a dropdown or a new screen with recent notifications.
- **`[👤]` (User Avatar):** Opens a dropdown with links to the Profile/Settings and Logout.

### 2.2. Slide-Out Navigation Menu

Activated by the hamburger icon, this menu slides in from the left, overlaying the content.

**Animation:**
- **Menu Container:** Slides in from the left (`translateX(0)` from `translateX(-100%)`). Duration: 300ms, Easing: `ease-out`.
- **Overlay:** Fades in (`opacity(1)` from `opacity(0)`) behind the menu to dim the main content.

**ASCII Wireframe (Menu Open):**
```
┌──────────────────┬───────────────────────────────┐
│ Logo             │                               │
├──────────────────┤ [✕] Close                     │
│ Dashboard        │                               │
│ My Resumes       │                               │
│ Analytics        │ Main Content (Dimmed)         │
│ Integrations     │                               │
├──────────────────┤                               │
│ Settings         │                               │
│ Logout           │                               │
└──────────────────┴───────────────────────────────┘
```

## 3. Screen Designs

### 3.1. Dashboard

The mobile dashboard provides an at-a-glance overview of the user's status and recent activity.

**Layout:** A single-column vertical feed.

**ASCII Wireframe:**
```
┌──────────────────────────────────────────┐
│ Dashboard                                │
├──────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────────┐  │
│  │ Resume Score: 88%  (▲ 5%)          │  │
│  └────────────────────────────────────┘  │
│                                          │
│  Recent Activity                         │
│  ┌────────────────────────────────────┐  │
│  │ ● New feedback on "Senior SWE"     │  │
│  │   2 hours ago                      │  │
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │ ✓ "Data Scientist" resume analyzed │  │
│  │   1 day ago                        │  │
│  └────────────────────────────────────┘  │
│                                          │
│                                      [+] │
└──────────────────────────────────────────┘
```

**Components:**
- **Stat Card (`Resume Score`):** A prominent card at the top displaying the primary KPI. It should be touch-friendly, perhaps flipping to reveal more details.
- **Activity List:** A list of recent events, rendered as individual cards. Each card is a touch target leading to the relevant detail view.
- **Floating Action Button (FAB) `[+]`:** A sticky button for the primary action, like "Analyze New Resume". This provides immediate access to the app's core function.

**Animations:**
- **Initial Load:** Use skeleton loaders for the stat card and activity list.
- **List Entrance:** The activity cards will animate in with a staggered fade-in and slide-up effect. (From `animations-specialist`: `staggerChildren`).
- **FAB:** The FAB will have a subtle scale-up on press for touch feedback.

### 3.2. Profile & Settings Section

This section will be a single, scrollable screen, using list views for clarity and ease of use.

**Layout:** Grouped list items.

**ASCII Wireframe:**
```
┌──────────────────────────────────────────┐
│ Settings                                 │
├──────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────────┐  │
│  │  [👤]  John Doe                     │  │
│  │        john.doe@email.com          │  │
│  └────────────────────────────────────┘  │
│                                          │
│  ACCOUNT                                 │
│  ┌────────────────────────────────────┐  │
│  │ Edit Profile                    >  │  │
│  ├────────────────────────────────────┤  │
│  │ Change Password                 >  │  │
│  └────────────────────────────────────┘  │
│                                          │
│  NOTIFICATIONS                           │
│  ┌────────────────────────────────────┐  │
│  │ Push Notifications              [toggle] │
│  ├────────────────────────────────────┤  │
│  │ Email Notifications             [toggle] │
│  └────────────────────────────────────┘  │
│                                          │
│  [ Logout Button ]                       │
│                                          │
└──────────────────────────────────────────┘
```

**Components:**
- **User Header:** A non-interactive header displaying the user's avatar, name, and email.
- **Setting Groups:** Use section headers (`ACCOUNT`, `NOTIFICATIONS`) to group related settings.
- **List Items:** Each setting is a list item.
    - **Navigation Items (`>`):** Tapping navigates to a new screen (e.g., "Edit Profile").
    - **Toggle Items (`[toggle]`):** For boolean settings like enabling/disabling notifications.

**Animations:**
- **Screen Transition:** When navigating to a sub-page (e.g., "Edit Profile"), the new screen will slide in from the right, pushing the current screen to the left. This is a standard native mobile pattern.

## 4. Implementation Details (for Developers)

- **Responsive Logic:**
    - Use Tailwind CSS responsive prefixes (`sm:`, `md:`, `lg:`).
    - The main layout component will use `flex-col` on mobile and `md:flex-row` for desktop.
    - The sidebar will be hidden by default (`hidden`) and shown on larger screens (`md:block`). The hamburger menu will be visible only on mobile (`md:hidden`).
    - Example: `<div class="md:hidden">Mobile Nav</div> <div class="hidden md:block">Desktop Sidebar</div>`

- **Component Adaptation:**
    - **Tables:** Data tables on desktop should transform into a list of cards on mobile. Each row becomes a card.
    - **Forms:** Ensure all forms are single-column on mobile for usability.

- **Data Fetching:**
    - Continue using `TanStack Query`. No changes are needed, but ensure skeleton loading states are implemented for a better mobile UX, as network latency can be higher.

- **Animation Implementation:**
    - Use `Framer Motion` for complex animations like the staggered list and slide-out menu. It provides excellent gesture and animation support.
    - For simple transitions like button feedback and color changes, use Tailwind's built-in transition utilities.

## 5. Agent Contributions Summary

- **`ui-designer`**: Provided the core layout patterns (top-nav), component styles, and design tokens.
- **`ux-researcher`**: Guided the focus on action-oriented design and prioritizing key mobile tasks.
- **`animations-specialist`**: Informed the choice of performant, mobile-friendly animations and interaction feedback.
- **`frontend-developer` & `fullstack-developer`**: Provided the technical foundation (React, Next.js, Tailwind) and data-fetching patterns (`TanStack Query`).
- **`mobile-app-builder`**: Reinforced mobile-native UX patterns like tab bars, native-style screen transitions, and the importance of touch feedback.
- **`integration-engineer`**: Influenced the simplified "Integrations" section within the settings, suggesting a list view for connected apps.
