#!/usr/bin/env python3
"""
Mock Test Simulator — Uses proper API calls
---------------------------------------------
Replicates exact user flow:
  1. Login → get JWT token
  2. POST /api/v1/tests/generate → generates 90 real questions via HDBSCAN
  3. Simulate answering (mix of correct/incorrect based on target accuracy)
  4. POST /api/v1/tests/submit → triggers full pipeline:
     - AnalyticsService.process_mock_submission (scoring, weak/strong areas)
     - SpacedRepetitionService.update_knowledge_graph (Neo4j STUDIED edges)
     - MongoDB user_progress collection update
     - MongoDB mock_tests status → completed

Usage:
  python3 scripts/seed_mock_tests.py              # Run 1 test with default settings
  python3 scripts/seed_mock_tests.py --count 3     # Run 3 sequential tests
  python3 scripts/seed_mock_tests.py --accuracy 0.7 # 70% correct answers
"""

import requests
import random
import sys
import time

BASE = "http://localhost:8000"
EMAIL = "shreyashdheemar123@gmail.com"
PASSWORD = "shreyash123"

# ─── Helpers ─────────────────────────────────────────────

def login():
    """Step 1: Login exactly like the frontend does, then get real user_id."""
    print("  📡 Logging in...")
    resp = requests.post(f"{BASE}/api/v1/users/login", data={
        "username": EMAIL,
        "password": PASSWORD
    })
    if resp.status_code != 200:
        print(f"  ❌ Login failed ({resp.status_code}): {resp.text}")
        sys.exit(1)
    token = resp.json().get("access_token")
    
    # Get real user_id from /me endpoint
    me_resp = requests.get(f"{BASE}/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    if me_resp.status_code == 200:
        user_id = me_resp.json().get("user_id", "temp")
    else:
        user_id = "temp"
    print(f"  ✅ Authenticated as user: {user_id}")
    return token, user_id


def generate_test(token, user_id):
    """Step 2: Generate a mock test via the real API (same as clicking 'Proceed to Secure Platform')."""
    print("  📝 Generating mock test (this may take a while due to HDBSCAN)...")
    resp = requests.post(
        f"{BASE}/api/v1/tests/generate",
        json={"user_id": user_id, "subjects": ["Physics", "Chemistry", "Mathematics"]},
        headers={"Authorization": f"Bearer {token}"},
        timeout=300  # 5 minutes max - HDBSCAN can be slow
    )
    if resp.status_code != 200:
        print(f"  ❌ Generation failed ({resp.status_code}): {resp.text[:200]}")
        return None, None

    data = resp.json()
    test_id = data["test_id"]

    # Flatten all questions with subject info
    questions = []
    for subject, qlist in data.get("questions_by_subject", {}).items():
        for q in qlist:
            q["_subject"] = subject
            questions.append(q)

    print(f"  ✅ Generated test {test_id[:8]}... with {len(questions)} questions")
    return test_id, questions


def simulate_answers(questions, accuracy):
    """Step 3: Simulate a student answering — exactly like clicking options on the frontend."""
    answers = []
    stats = {"correct": 0, "incorrect": 0, "by_subject": {}}

    # Pre-calculate a fixed pool of time (2 hours to 2h45m max, strictly under 3 hours = 10800s)
    total_time_pool = random.randint(7200, 9900)
    weights = [random.uniform(0.5, 2.0) for _ in questions]
    total_weight = sum(weights)

    for i, q in enumerate(questions):
        subj = q.get("_subject", "unknown")
        if subj not in stats["by_subject"]:
            stats["by_subject"][subj] = {"correct": 0, "incorrect": 0}

        should_correct = random.random() < accuracy

        if q.get("type") == "mcq":
            correct_opts = q.get("correct_options", [])
            all_opts = [o.get("identifier", "A") for o in q.get("options", [])]

            if should_correct and correct_opts:
                selected = correct_opts[0]
                is_correct = True
            else:
                wrong = [o for o in all_opts if o not in correct_opts]
                selected = random.choice(wrong) if wrong else (correct_opts[0] if correct_opts else "A")
                is_correct = selected in correct_opts
        else:
            # Integer/numerical type
            correct_val = str(q.get("correct_answer") or q.get("answer") or "0")
            if should_correct:
                selected = correct_val
                is_correct = True
            else:
                selected = str(random.randint(-10, 100))
                is_correct = (selected == correct_val)

        if is_correct:
            stats["correct"] += 1
            stats["by_subject"][subj]["correct"] += 1
        else:
            stats["incorrect"] += 1
            stats["by_subject"][subj]["incorrect"] += 1

        allocated_time = int((weights[i] / total_weight) * total_time_pool)

        answers.append({
            "question_id": q["question_id"],
            "is_correct": is_correct,
            "time_spent": max(10, allocated_time),
            "selected_option": selected
        })

    return answers, stats


def submit_test(token, user_id, test_id, answers):
    """Step 4: Submit test via API (same as clicking 'Submit Test' on frontend).
    This triggers the full backend pipeline:
      - AnalyticsService scoring
      - Neo4j knowledge graph updates
      - MongoDB user_progress writes
    """
    print("  🚀 Submitting test...")
    resp = requests.post(
        f"{BASE}/api/v1/tests/submit",
        json={"user_id": user_id, "test_id": test_id, "answers": answers},
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout=120
    )
    if resp.status_code != 200:
        print(f"  ❌ Submission failed ({resp.status_code}): {resp.text[:200]}")
        return None

    result = resp.json()
    print(f"  ✅ Submitted! Score: {result.get('score')}/300")
    return result


# ─── Main Flow ───────────────────────────────────────────

def run_one_test(token, user_id, accuracy, test_num):
    """Run a complete test cycle via API calls."""
    print(f"\n{'─' * 50}")
    print(f"  🧪 TEST {test_num} (target accuracy: {accuracy*100:.0f}%)")
    print(f"{'─' * 50}")

    # Generate
    test_id, questions = generate_test(token, user_id)
    if not test_id:
        return None

    # Ping (like frontend does to keep test alive)
    requests.post(f"{BASE}/api/v1/tests/ping/{test_id}",
                  headers={"Authorization": f"Bearer {token}"})

    # Simulate answering
    print(f"  🎲 Simulating student answers...")
    answers, stats = simulate_answers(questions, accuracy)
    print(f"     Total: {stats['correct']}✅ {stats['incorrect']}❌")
    for subj, s in stats["by_subject"].items():
        total = s['correct'] + s['incorrect']
        pct = (s['correct'] / total * 100) if total else 0
        print(f"     {subj}: {s['correct']}/{total} ({pct:.0f}%)")

    # Submit
    result = submit_test(token, user_id, test_id, answers)
    return result


def main():
    count = 1
    base_accuracy = 0.55

    # Parse CLI args
    for i, arg in enumerate(sys.argv):
        if arg == "--count" and i + 1 < len(sys.argv):
            count = int(sys.argv[i + 1])
        if arg == "--accuracy" and i + 1 < len(sys.argv):
            base_accuracy = float(sys.argv[i + 1])

    print("=" * 55)
    print("  🧪 Solid4x Mock Test Simulator (API-based)")
    print("=" * 55)
    print(f"  Tests to run: {count}")
    print(f"  Base accuracy: {base_accuracy*100:.0f}%")

    # Login once
    token, user_id = login()

    results = []
    for i in range(count):
        # Vary accuracy across tests to show improvement
        if count > 1:
            # Scale from (base - 0.15) to (base + 0.15) across tests
            progress = i / (count - 1) if count > 1 else 0
            accuracy = (base_accuracy - 0.15) + progress * 0.30
            accuracy = max(0.2, min(0.95, accuracy))
        else:
            accuracy = base_accuracy

        result = run_one_test(token, user_id, accuracy, i + 1)
        if result:
            results.append(result)

        # Brief pause between tests
        if i < count - 1:
            print(f"\n  ⏳ Waiting 2s before next test...")
            time.sleep(2)

    # Summary
    print(f"\n{'=' * 55}")
    print(f"  📊 SIMULATION COMPLETE — {len(results)}/{count} tests submitted")
    print(f"{'=' * 55}")
    for i, r in enumerate(results):
        print(f"  Test {i+1}: Score {r.get('score')}/300")
    print(f"\n  💡 Refresh http://localhost:5173/mocktest to see results!")


if __name__ == "__main__":
    main()
