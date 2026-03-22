# Solid4x Frontend UI & Integration Guide

This document structurally outlines exactly how to build the React/Next.js UI interfaces to seamlessly consume the Solid4x Backend APIs natively out of the box!

## 1. Authentication & Security
**Global State:** Use Redux Toolkit, Zustand, or React Context to track the strict `access_token` string. Every single Axios/Fetch request MUST intercept and explicitly inject the `Authorization: Bearer <token>` in its HTTP configuration scope.

**Components:**
- `LoginForm`: Collects email and password. Hits `POST /api/v1/users/login` using `FormData`, catching the returned JWT natively.
- `OnboardingWizard`: Hits `POST /api/v1/users/create` to create an entirely new tracking framework natively on sign-up algorithms.

## 2. Algorithmic Priority Study Dashboard
**Global State:** `plannerState` tracks the deterministic 7-day structural queue fetched mathematically overriding memory constraints.

**UI Flow:** The main landing workspace a student lands on after loading the platform.
**Components:**
- `DashboardGrid`: Mounts a visual block calendar parsing from `GET /api/v1/planner/plan`. 
- `ToDoWidget`: Iterates directly over the `"pending"` sessions locally. When the student clicks a checkbox, it strictly fires `PATCH /api/v1/planner/session/{session_id}` passing `{"status": "done"}`.

## 3. Flashcard Retention Engine
**UI Flow:** Dedicated `FlashcardArena` workspace built specifically to run atomic drills smoothly.

**Components:**
- `ReviewDeck`: Sequentially loops over arrays fetched natively from `GET /api/v1/flashcards/due`. 
- `SM2Card`: Displays the target topic. On button flip, the student is presented 5 specific gradient grading buttons. Upon grading their memory 0-5, it fires `POST /api/v1/flashcards/review` with `{"quality": X}`. Updates global mastery score natively.

## 4. The Neo4j Untouched Syllabus Map
**UI Flow:** Exists as a "New Topics To Cover" widget natively inside the core workspace.
**Components:**
- `UnstudiedTracker`: Hits `GET /api/v1/repetition/unpracticed?subject=Physics`. Parses the raw array and explicitly auto-generates clickable buttons to instantly dive directly into unpracticed domains.

## 5. Topographical Mock Test Arena
**Global State:** `testState` heavily caches the 75-question structurally biased mock packages.

**UI Flow:** Dedicated Test Taking sandbox enforcing identical JEE aesthetics and locking interfaces natively.
**Components:**
- `GenerateTestModal`: Interactive subject-blocking checkboxes strictly hitting `POST /api/v1/tests/generate`.
- `LiveTestWorkspace`: A heavily optimized React timer interface strictly locking active browser panels and continuously mutating arrays matching MCQs vs NVQs. 
- `SubmissionHandler`: On test wrap, assembles the `PayloadObj` JSON map calculating `is_correct` natively, firing one final large network call explicitly to `POST /api/v1/tests/submit` caching the weak area metrics.

## 6. Analytics & Re-Drill System
**UI Flow:** The final visualization graph loaded immediately chronologically post-submission payload blocks.
**Components:**
- `AnalyticsDashboard`: Queries `GET /api/v1/tests/history`. Loops the nested JSON mapping `score`, `weak_areas`, and `strong_areas` to construct explicit frontend SVG/Recharts visual radial nodes natively.
- `KNN-Remediation`: Actively intercepts visually failed questions and exposes a native "Learn Similar Content" string block. If clicked, directly fetches K-NN targets dynamically fetching similarly identical topologies safely without mutating structural bounds via `POST /api/v1/practice/similar`!
