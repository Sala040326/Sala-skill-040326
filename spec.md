# Technical Specification: Artistic Agentic Flow System

**Version:** 1.1.0  
**Date:** October 26, 2023  
**Status:** Approved  
**Author:** Senior Frontend Engineer / Architect

---

## 1. Executive Summary

### 1.1 Project Overview
**Artistic Agentic Flow** is a cutting-edge web application that merges enterprise-grade batch document processing with an avant-garde user interface experience. Unlike traditional, utilitarian administrative dashboards, this application introduces the concept of "Artistic Intelligence," wrapping powerful AI workflows in a dynamic, theme-able UI inspired by 20 of history's greatest painters.

The system is designed to leverage the Google Gemini API (specifically the Gemini 2.5 and 3.0 series) to perform complex text analysis, summarization, agentic reasoning chains, and compliance checks. It features a fully configurable pipeline, a "Chain of Thought" agent builder, and real-time system logging, all while allowing the user to toggle between "Monet," "Picasso," "Cyberpunk (Warhol)," and other visual styles instantly.

### 1.2 Vision and Goals
*   **Human-Centric AI:** To make interacting with LLMs feel organic, creative, and visually stimulating rather than sterile.
*   **Configurability:** To empower users to define their own processing pipelines and agent behaviors without touching code.
*   **Transparency:** To provide real-time visualization of system logs, token usage, and processing states.
*   **Accessibility:** To support multi-language interfaces (English and Traditional Chinese) and light/dark modes natively.

### 1.3 Scope
This specification covers the frontend architecture, state management, UI/UX theming engine, Gemini API integration, and the functional logic for the Dashboard, Pipeline, Agents, Brain, Note Keeper, and Officer Tools modules.

---

## 2. System Architecture

### 2.1 High-Level Design
The application is a Single Page Application (SPA) built using **React 19**. It operates entirely client-side, managing state via the React Context API and utilizing the browser's local execution environment to handle logic. It connects directly to the Google Gemini API for intelligence tasks.

*   **Presentation Layer:** React components styled with Tailwind CSS, leveraging Framer Motion for complex animations (page transitions, list reordering, loading states).
*   **Logic Layer:** TypeScript interfaces and functional components handling business logic (pipeline iteration, agent chaining).
*   **Service Layer:** A dedicated `geminiService` module that abstracts the `@google/genai` SDK, handling authentication and error management.
*   **State Management:** A global `AppContext` provider that broadcasts theme, language, and logging data to all components.

### 2.2 Technology Stack
*   **Core Framework:** React 19 (`react`, `react-dom`)
*   **Build Tooling:** ES Modules via `esm.sh` (No build step required for this implementation, strictly browser-native ES6 imports).
*   **Styling:** Tailwind CSS (via CDN) for utility classes; Custom CSS for scrollbars.
*   **Icons:** Lucide React for consistent, vector-based iconography.
*   **Animations:** Framer Motion for layout animations and presence management.
*   **AI Integration:** Google GenAI SDK (`@google/genai` v1.38.0).
*   **Fonts:** Google Fonts (Cinzel, Inter, Playfair Display, Space Mono).

### 2.3 Component Diagram
The application is structured around a central `App` component that serves as the layout shell, containing the `Header`, `Sidebar` (Navigation), and the `MainContent` area.

```text
App (Context Provider)
│
├── Header
│   ├── Logo & Title
│   ├── Jackpot Trigger (Random Theme)
│   ├── Theme Selector (Dropdown)
│   ├── Language Toggle
│   └── Dark/Light Mode Toggle
│
├── Sidebar Navigation
│   ├── Dashboard Tab
│   ├── Pipeline Tab
│   ├── Agents Tab
│   ├── Brain Tab
│   ├── Notes Tab
│   └── Officer Tab
│
└── Main Content Area (AnimatePresence)
    ├── DashboardView (Stats, Charts, Logs)
    ├── PipelineView (File Upload, Step Config, Progress)
    ├── AgentsView (Input Data, Step Chain, Editable Output)
    ├── BrainView (Chat Interface)
    ├── NoteKeeperView (Text Editor + AI Tools)
    └── OfficerToolsView (Compliance Workflows)
