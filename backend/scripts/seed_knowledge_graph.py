#!/usr/bin/env python3
"""
Direct Neo4j Knowledge Graph Seeder
-------------------------------------
Bypasses the slow HDBSCAN test generation pipeline.
Directly calls the backend APIs to simulate practice submissions
for various topics, creating a realistic mix of:
  - Mastered topics (many correct answers, high strength)
  - Weak topics (mostly incorrect, low strength)  
  - Due topics (practiced long ago - simulated by direct Neo4j writes)
  - Unpracticed topics (never touched - already exist from curriculum ingestion)

Usage: python3 scripts/seed_knowledge_graph.py
"""

import requests
import random
import sys

BASE = "http://localhost:8000"
EMAIL = "shreyashdheemar123@gmail.com"
PASSWORD = "shreyash123"

def login():
    resp = requests.post(f"{BASE}/api/v1/users/login", data={
        "username": EMAIL, "password": PASSWORD
    })
    if resp.status_code != 200:
        print(f"❌ Login failed: {resp.text}")
        sys.exit(1)
    token = resp.json()["access_token"]
    print(f"✅ Logged in. Token: {token[:25]}...")
    return token

def fetch_questions_for_topic(token, topic, limit=5):
    """Fetch practice questions for a specific topic."""
    resp = requests.get(
        f"{BASE}/api/v1/practice/generate",
        params={"topic": topic, "limit": limit},
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )
    if resp.status_code == 200:
        return resp.json()
    return []

def submit_practice(token, question_id, is_correct):
    """Submit a single practice answer."""
    resp = requests.post(
        f"{BASE}/api/v1/practice/submit",
        json={
            "user_id": "temp",
            "question_id": question_id,
            "is_correct": is_correct,
            "time_spent": random.randint(30, 180)
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        timeout=15
    )
    return resp.status_code == 200

def main():
    print("=" * 60)
    print("🌱 Solid4x Knowledge Graph Seeder")
    print("=" * 60)
    
    token = login()
    
    # Topics to practice with different strategies
    # Format: (topic_slug, correct_ratio, num_questions)
    scenarios = [
        # MASTERED: High correct ratio, many attempts -> strength >= 3.0
        ("projectile-motion", 1.0, 5),
        ("quadratic-equation-and-inequalities", 0.9, 5),
        ("mole-concept", 1.0, 5),
        ("electric-flux-and-gauss-law", 0.8, 5),
        
        # WEAK: Low correct ratio -> strength < 1.5
        ("wave-optics", 0.0, 3),
        ("polymers", 0.2, 3),
        ("rotational-motion", 0.1, 3),
        
        # MEDIUM (will become "due" after time passes): 
        ("thermodynamics-process", 0.6, 4),
        ("definite-integration", 0.5, 4),
        ("chemical-kinetics-and-nuclear-chemistry", 0.7, 3),
    ]
    
    total_submitted = 0
    
    for topic, correct_ratio, limit in scenarios:
        print(f"\n📚 Practicing: {topic} (target {correct_ratio*100:.0f}% correct, {limit} questions)")
        
        questions = fetch_questions_for_topic(token, topic, limit)
        if not questions:
            print(f"   ⚠️  No questions found for '{topic}', skipping.")
            continue
        
        correct = 0
        incorrect = 0
        for q in questions:
            is_correct = random.random() < correct_ratio
            ok = submit_practice(token, q["question_id"], is_correct)
            if ok:
                total_submitted += 1
                if is_correct:
                    correct += 1
                else:
                    incorrect += 1
            else:
                print(f"   ⚠️  Failed to submit {q['question_id']}")
        
        print(f"   ✅ {correct} correct, ❌ {incorrect} incorrect")
    
    print(f"\n{'=' * 60}")
    print(f"🎉 SEEDING COMPLETE! Submitted {total_submitted} practice answers.")
    print(f"{'=' * 60}")
    print(f"\n💡 Now visit http://localhost:5173/retention to see:")
    print(f"   🟢 Mastered: projectile-motion, quadratic-equation, mole-concept, etc.")
    print(f"   🔴 Weak: wave-optics, polymers, rotational-motion")
    print(f"   🟡 Due: (will appear after time passes for medium-strength topics)")
    print(f"   ⚪ Unexplored: all other topics in the curriculum")

if __name__ == "__main__":
    main()
