import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_tutor.generator import generate_answer


def main():
    print("=" * 60)
    print("  AI Tutor - JEE Doubt Solver (RAG)")
    print("  Type your doubt and press Enter")
    print("  Commands: /quit /sources")
    print("=" * 60)
    show_sources = True

    while True:
        try:
            query = input("\nYour doubt: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if not query:
            continue

        if query.lower() in ("/quit", "/exit", "/q"):
            print("Exiting.")
            break

        if query.lower() == "/sources":
            show_sources = not show_sources
            state = "ON" if show_sources else "OFF"
            print(f"Source display: {state}")
            continue

        start = time.time()
        try:
            result = generate_answer(query)
        except Exception as e:
            print(f"\nError: {e}")
            continue

        elapsed = time.time() - start

        print(f"\n{'=' * 60}")
        print(result["answer"])
        print(f"{'=' * 60}")

        if show_sources and result["sources"]:
            print("\nSources:")
            for src in result["sources"]:
                print(f"  - {src}")

        print(f"\n[{result['num_chunks_retrieved']} chunks retrieved, "
              f"{result['num_chunks_used']} used | {elapsed:.1f}s]")


if __name__ == "__main__":
    main()
