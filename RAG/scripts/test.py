import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_tutor.generator import generate_answer

def test():
    query = "explain example 1.11 from the 1.6 Algebra cengage 12 maths page 18"
    result = generate_answer(query)
    print(result["answer"])

if __name__ == "__main__":
    test()
