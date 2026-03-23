#!/usr/bin/env python3
"""
Solid4x Mock Test Simulator
----------------------------
This script simulates a full mock test lifecycle:
1. Logs in to get a JWT token
2. Generates a 90-question mock test
3. Auto-answers questions (some correct, some incorrect)
4. Submits the test, which populates:
   - MongoDB user_progress collection
   - Neo4j knowledge graph (STUDIED relationships with strength values)

Usage:
  python3 simulate_test.py --email <email> --password <password>
  
  Or edit EMAIL/PASSWORD below.
"""

import requests
import random
import sys

BASE = "http://localhost:8000"

# ──── Config ────
EMAIL = "shreyashdheemar123@gmail.com"
PASSWORD = "shreyash123"

# Fraction of questions to answer correctly (0.0 - 1.0)
# 0.5 means ~50% correct, ~50% incorrect
CORRECT_RATIO = 0.55

def login(email, password):
    """Authenticate and return JWT token."""
    resp = requests.post(f"{BASE}/api/v1/users/login", data={
        "username": email,
        "password": password
    })
    if resp.status_code != 200:
        print(f"❌ Login failed ({resp.status_code}): {resp.text}")
        sys.exit(1)
    token = resp.json().get("access_token")
    print(f"✅ Logged in successfully. Token: {token[:20]}...")
    return token

def generate_test(token):
    """Generate a 90-question mock test."""
    resp = requests.post(f"{BASE}/api/v1/tests/generate", 
        json={"user_id": "temp", "subjects": ["Physics", "Chemistry", "Mathematics"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    if resp.status_code != 200:
        print(f"❌ Test generation failed ({resp.status_code}): {resp.text}")
        sys.exit(1)
    
    data = resp.json()
    test_id = data["test_id"]
    
    questions = []
    for subject, qlist in data["questions_by_subject"].items():
        for q in qlist:
            q["_subject"] = subject
            questions.append(q)
    
    print(f"✅ Generated test {test_id} with {len(questions)} questions")
    return test_id, questions

def auto_answer(questions, correct_ratio):
    """
    Simulate answering questions.
    For MCQs: pick the correct option or a random wrong one.
    For integer: use the correct answer or a random wrong number.
    """
    answers = []
    stats = {"correct": 0, "incorrect": 0, "by_subject": {}}
    
    for q in questions:
        subj = q.get("_subject", "unknown")
        if subj not in stats["by_subject"]:
            stats["by_subject"][subj] = {"correct": 0, "incorrect": 0}
        
        should_be_correct = random.random() < correct_ratio
        
        if q.get("type") == "mcq":
            correct_options = q.get("correct_options", [])
            all_options = [opt["identifier"] for opt in q.get("options", [])]
            
            if should_be_correct and correct_options:
                selected = correct_options[0]
                is_correct = True
            else:
                wrong = [o for o in all_options if o not in correct_options]
                selected = random.choice(wrong) if wrong else (correct_options[0] if correct_options else "A")
                is_correct = selected in correct_options
        else:
            # Integer / numerical
            correct_answer = str(q.get("correct_answer") or q.get("answer") or "0")
            if should_be_correct:
                selected = correct_answer
                is_correct = True
            else:
                selected = str(random.randint(-10, 100))
                is_correct = (selected == correct_answer)
        
        if is_correct:
            stats["correct"] += 1
            stats["by_subject"][subj]["correct"] += 1
        else:
            stats["incorrect"] += 1
            stats["by_subject"][subj]["incorrect"] += 1
        
        answers.append({
            "question_id": q["question_id"],
            "is_correct": is_correct,
            "time_spent": random.randint(30, 300),
            "selected_option": selected
        })
    
    return answers, stats

def submit_test(token, test_id, answers):
    """Submit the answered test."""
    resp = requests.post(f"{BASE}/api/v1/tests/submit",
        json={"user_id": "temp", "test_id": test_id, "answers": answers},
        headers={"Authorization": f"Bearer {token}"}
    )
    if resp.status_code != 200:
        print(f"❌ Submission failed ({resp.status_code}): {resp.text}")
        sys.exit(1)
    
    result = resp.json()
    print(f"✅ Test submitted! Score: {result.get('score')}")
    return result

def main():
    # Parse optional CLI args
    email, password = EMAIL, PASSWORD
    for i, arg in enumerate(sys.argv):
        if arg == "--email" and i + 1 < len(sys.argv):
            email = sys.argv[i + 1]
        if arg == "--password" and i + 1 < len(sys.argv):
            password = sys.argv[i + 1]
    
    print("=" * 60)
    print("🧪 Solid4x Mock Test Simulator")
    print("=" * 60)
    
    # Step 1: Login
    print("\n📡 Step 1: Authenticating...")
    token = login(email, password)
    
    # Step 2: Generate test
    print("\n📝 Step 2: Generating mock test...")
    test_id, questions = generate_test(token)
    
    # Step 3: Auto-answer
    print(f"\n🎲 Step 3: Simulating answers ({CORRECT_RATIO*100:.0f}% target accuracy)...")
    answers, stats = auto_answer(questions, CORRECT_RATIO)
    
    print(f"   Total: {stats['correct']} correct, {stats['incorrect']} incorrect")
    for subj, s in stats["by_subject"].items():
        print(f"   {subj}: {s['correct']}✅  {s['incorrect']}❌")
    
    # Step 4: Submit
    print("\n🚀 Step 4: Submitting test (this updates MongoDB + Neo4j)...")
    result = submit_test(token, test_id, answers)
    
    print("\n" + "=" * 60)
    print("✅ SIMULATION COMPLETE")
    print("=" * 60)
    print(f"   Final Score : {result.get('score')}")
    print(f"   Weak Areas  : {list(result.get('weak_areas', {}).keys())}")
    print(f"   Strong Areas: {list(result.get('strong_areas', {}).keys())}")
    print("\n💡 Now visit http://localhost:5173/retention to see updated categories!")
    print("   - Topics you got wrong → Weak Areas")
    print("   - Topics with 3+ correct answers → Mastered (after multiple tests)")
    print("   - Topics with decaying retention → Due for Review (after some time)")

if __name__ == "__main__":
    main()
