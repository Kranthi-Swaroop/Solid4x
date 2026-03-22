# Solid4x Core Architecture & Feature Documentation

This document outlines the advanced technical features operating under the hood of the Solid4x Core API Backend, built heavily on FastAPI, MongoDB, ChromaDB, and Neo4j.

## 1. Topologically Accurate Mock Test Generation
`POST /api/v1/tests/generate`

**How it works:**
The test generator strictly enforces a standard topology (20 Multiple Choice Questions, 10 Numerical Value Questions per subject). 
When a test is requested, the system automatically pulls a large candidate pool of ~150 questions per subject from MongoDB. 
To ensure that a student does not receive two mathematically identical questions in the same test, it calculates the high-dimensional Vector Embeddings of every candidate utilizing **ChromaDB**. It then applies an advanced **HDBSCAN Density Clustering** algorithm to visually group geometrically identical patterns together. The API then sequentially samples exactly one question from each dense mathematical cluster, resulting in a perfectly variance-controlled 90-question test paper.

## 2. Adaptive Practice & Remediation Engine
The practice engine exposes two distinct routing modalities explicitly built for distinct student workflows:

- **The Drill Generator** (`GET /api/v1/practice/generate`):
  If the student actively clicks on a chapter (like "Thermodynamics") and wants to drill concepts, we use the Drill Generator. You pass it `chapter` and `topic` parameters. The backend inherently queries MongoDB, aggressively isolates `$nin` any questions the student has formally solved correctly in the past, and returns exactly 5 fresh, mathematically unseen PyQs native strictly to that chapter limit without triggering vector comparisons.

- **Dynamic K-NN Vectors** (`POST /api/v1/practice/similar`):
  Used strictly as an analytical remediation layer. If a student natively struggles or gets Question #14 wrong on a Mock Test, they can click "Learn Similar Concept". The API extracts the $1024D$ mathematical tensor embedding for Question #14 from ChromaDB. It executes a strict **K-Nearest-Neighbor (K-NN)** similarity search actively across all 15,000 equations, over-fetches the closest 100 mathematical neighbors, and surgically filters them across MongoDB to explicitly restrict the returned questions perfectly to the same target domain (e.g. Physics -> Rotational Motion) so the student learns the identical logic footprint instantly.

## 3. Neo4j Learner Knowledge Graphs
`POST /api/v1/practice/submit` & `POST /api/v1/tests/submit`

**How it works:**
Every single interaction a student has with any question on Solid4x is captured entirely.
The backend maintains a heavily scalable Graph Node Database in **Neo4j**. When a student submits a mock test (75 questions), the API traverses their specific Neo-Profile node and logically maps or destructs Relationship vectors `[STUDIED]` between the student and every unique subject, chapter, and topic. Correct answers permanently strengthen this mathematical bond, while incorrect answers fracture to map vulnerabilities intuitively.

## 4. Exponential Spaced Repetition (The Forgetting Curve)
`GET /api/v1/repetition/reviews/due/{user_id}`

**How it works:**
We actively track human memory decay using the biological formula $R = e^{-t / s}$, where $t$ is time passed and $s$ is historical conceptual strength.
A complex Cypher Query continuously cycles across a student's Neo4j node graph. Any topic where the structural Retention $R$ objectively falls below an arbitrary ~70% threshold is immediately flagged as a `"Due Topic"`. The frontend dynamically retrieves this array to explicitly prompt the student to review it right before they forget it.

## 5. System-Wide Adaptive Bias
**How it works:**
The Test Generator and Practice Generator systems are highly entangled with the student's Spaced Repetition engine.
1. **Never Repeat (`$nin`)**: The system universally fetches all `question_id`s that the student has ever correctly answered from MongoDB and automatically bans them from ever showing up in future test generation pipelines.
2. **Weakness Injection:** When generating a Mock Test, the generator natively asks Neo4j for the student's heavily decayed "Due Topics". It aggressively prioritizes injecting those highly vulnerable subjects specifically into the Mock Test parameters, meaning the more mock tests the student takes, the faster their specific weaknesses literally disappear.

## 6. Real-time Mock Analytics & Concept Solving
`POST /api/v1/analysis/mock` & `POST /api/v1/solver/explain`

**How it works:**
When a student ultimately submits a mock test, the backend calculates the absolute score mathematically conforming to actual Modern JEE Negative Marking rules (+4 / -1 / 0). Simultaneously, it iterates across the aggregate chapters and explicitly returns dict-arrays containing `<50%` weak accuracy groupings natively.
Finally, when a student needs to understand where they went wrong, the `/solver` endpoint organically maps to the structurally vetted dataset text explanations immediately locally instead of risking VLM LLM hallucinations.

## 7. Static Curriculum Knowledge Base
`GET /api/v1/repetition/unpracticed/{user_id}?subject=physics`

**How it works:**
Instead of relying on flat `.json` syllabus lists, the entirety of the 15,000 document database curriculum has been logically mapped inside Neo4j as a static structural tree.
If the frontend needs to understand what portions of the syllabus a student has untouched, the API executes a pure Cypher network `$nin` exclusion (`WHERE NOT EXISTS`). The API instantly traces every `Topic` node tied to the requested `$subject` natively that lacks a `[:STUDIED]` relationship bound to that specific user ID natively, returning precisely the entirely unbounded "Unstudied Curriculum."

## 8. User Management Identity Core
`POST /api/v1/users/create` & `GET /api/v1/users/{user_id}`

**How it works:**
The User Service Controller maintains a dedicated `users` collection in MongoDB alongside vector tests and analytics. To create a sample user or register a genuine dashboard user, submit an `email`, `username`, and `password` payload. The API natively intercepts it, enforces uniqueness via MongoDB aggregation checks to prevent metadata ghosting, constructs a robust tracking environment, and emits a permanent string `user_id` mapped synchronously to all downstream analytics pipelines and Spaced Repetition profiles!
