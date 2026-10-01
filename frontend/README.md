<div align="center">

# 🧭 ContribPilot

**AI-powered GitHub contribution assistant.**
Discover issues, understand codebases, and get guided hints for your open-source contributions.

![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-build-646CFF?logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS-06B6D4?logo=tailwindcss&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Key Components](#key-components)
- [Design System](#design-system)
- [Security](#security)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

ContribPilot helps contributors find GitHub issues that match their skills and experience level. It uses AI to analyze each issue, break it into actionable steps, and provide progressive hints so you can solve it without having the answer handed to you.

> **Note:** This repository is the **frontend**. It requires a running ContribPilot **FastAPI backend** (see [Prerequisites](#prerequisites)).

## Features

| | Feature | Description |
|---|---------|-------------|
| 🔍 | **Issue Matchmaker** | Find GitHub issues that match your skills and experience level |
| 📊 | **Match Scoring** | Visual scores showing how well each issue fits your profile |
| 🧩 | **AI Issue Breakdown** | Problem summary, files to inspect, relevant symbols, and investigation steps |
| 💡 | **Guided Hints** | Three levels of progressive hints for when you get stuck |
| ⚙️ | **Configurable** | Bring your own GitHub token and LLM API key |
| 🔒 | **Local credentials** | Stored in your browser and never displayed after saving |

## Tech Stack

| Category | Technology |
|----------|------------|
| Framework | React 18+ |
| Routing | React Router v6 |
| Animation | Framer Motion |
| Icons | Lucide React |
| Styling | Tailwind CSS |
| Build tool | Vite |
| API | FastAPI backend (external) |

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Access to a ContribPilot API backend

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/contribpilot.git
cd contribpilot

# Install dependencies
npm install

# Point the app at your backend
echo "VITE_API_URL=http://localhost:8000" > .env

# Start the development server
npm run dev
```

### Production Build

```bash
npm run build
npm run preview
```

## Configuration

Open the **Configuration** page (`/config`) to set up your credentials.

### GitHub Personal Access Token

Required for accessing repositories and issues.

1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens).
2. Generate a new token with the `repo` and `read:org` scopes.
3. Paste it into the **GitHub Configuration** field.

### LLM API Key

Required for AI-powered matching, breakdowns, and hints.

- Supports Groq API keys (format: `gsk_••••••••`).

> **⚠️ Security note:** Credentials are stored in `localStorage` and sent to the backend via request headers (`X-Github-Token`, `X-Groq-Api-Key`). Never commit credentials to version control.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `""` (same origin) |

## Usage

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Repository │ →  │   Skills    │ →  │ Find Issues │ →  │   Match     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
                                                                ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Hints     │ ←  │  Breakdown  │ ←  │Issue Details│ ←  │Select Issue │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

1. **Choose a repository** — enter it as `owner/repo` (e.g. `ejwa/gitinspector`).
2. **Enter your skills** — comma-separated (e.g. `python, git, pytest`).
3. **Select your level** — Beginner, Intermediate, or Advanced.
4. **Find issues** — click **Find Issue** to search for matching contributions.
5. **Explore matches** — review issue cards with match scores and AI reasoning.
6. **Open an issue** — view the AI-generated breakdown.
7. **Understand the issue** — read the problem summary, files to inspect, symbols, and steps.
8. **Get hints** — request progressive hints (Level 1–3) when you're stuck.

## API Reference

The frontend talks to a FastAPI backend through these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/issues/recommend` | `POST` | Find matching issues |
| `/api/issues/{id}/breakdown` | `POST` | Get an AI issue breakdown |
| `/api/contributions/hint` | `POST` | Get a progressive hint |

### Request Headers

```json
{
  "Content-Type": "application/json",
  "X-Github-Token": "<github_pat>",
  "X-Groq-Api-Key": "<llm_api_key>"
}
```

### Example: Find Issues

```http
POST /api/issues/recommend
```

```json
{
  "skills": ["python", "git", "pytest"],
  "experience": "beginner",
  "repo": "ejwa/gitinspector",
  "limit": 10
}
```

### Example: Get a Hint

```http
POST /api/contributions/hint
```

```json
{
  "level": 1,
  "issue_context": { },
  "current_progress": { }
}
```

## Project Structure

```
contribpilot/
├── src/
│   ├── components/
│   │   ├── GlobalBackground/
│   │   │   └── GlobalBackground.jsx
│   │   ├── HintCard.jsx          # Progressive hint UI
│   │   ├── IssueCard.jsx         # Issue display card
│   │   └── Navbar.jsx            # Navigation with step indicator
│   │
│   ├── pages/
│   │   ├── Home.jsx              # Landing page
│   │   ├── Matchmaker.jsx        # Issue search & results
│   │   ├── IssueDetails.jsx      # Issue breakdown view
│   │   ├── Config.jsx            # Credential configuration
│   │   └── Docs.jsx              # Documentation
│   │
│   ├── services/
│   │   └── api.js                # API client & endpoints
│   │
│   ├── utils/
│   │   └── sessions.js           # localStorage utilities
│   │
│   ├── App.jsx                   # Root component with routing
│   ├── main.jsx                  # Entry point
│   └── index.css                 # Global styles
│
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## Key Components

### `<IssueCard />`

- Repository and issue number
- Title and labels
- Match score (circular progress indicator)
- AI reasoning snippet
- "Start Issue" call to action

### `<HintCard />`

- Three collapsible hint levels
- Automatic JSON parsing for structured hints
- Special rendering for files, symbols, tests, and areas
- Error handling for empty responses

### `<Navbar />`

- Logo and branding
- Primary navigation links
- Current step indicator for the contribution flow
- GitHub connection status
- Settings shortcut

## Design System

### Color Palette

| Element | Color |
|---------|-------|
| Background | Dark `#0a0c10` |
| Primary accent | Violet `#8b5cf6` |
| Secondary accent | Cyan `#22d3ee` |
| Success | Green `#22c55e` |
| Error | Red `#ef4444` |
| Text primary | White `#ffffff` |
| Text muted | Slate `#94a3b8` |

### Typography

- **Headings:** system sans-serif, bold weights
- **Body / code:** monospace (`font-mono`)
- **Hero title:** Orbitron (futuristic display font)

### Component Patterns

- Rounded corners: `rounded-xl` to `rounded-2xl`
- Borders: `border-white/10`
- Glows: `shadow-[0_0_40px_-10px_rgba(139,92,246,0.2)]`
- Transitions: 200–300ms ease

## Security

1. **Local storage only** — credentials stay in your browser and are sent only to the configured API backend.
2. **No credential display** — saved tokens are never shown in the UI.
3. **Minimum permissions** — use tokens with the fewest scopes that work for you.
4. **No logging** — credentials are not written to the console.

## Development

```bash
npm run dev       # Start development server
npm run build     # Build for production
npm run preview   # Preview production build
npm run lint      # Run ESLint
```

## Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m "Add amazing feature"`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

Licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- [Lucide](https://lucide.dev/) for the icon set
- [Framer Motion](https://www.framer.com/motion/) for animations
- [Tailwind CSS](https://tailwindcss.com/) for utility-first styling
- [Vite](https://vitejs.dev/) for fast builds

---

<p align="center">
  <strong>ContribPilot</strong> — Navigate open source with confidence.
</p>