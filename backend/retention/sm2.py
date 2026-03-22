MIN_EASINESS = 1.3

def sm2(quality: int, repetitions: int, easiness: float, interval: int) -> dict:
    """
    quality   : int 0–5 (0=complete blackout, 5=perfect recall)
    repetitions: how many times this card has been reviewed
    easiness  : easiness factor, starts at 2.5
    interval  : current interval in days

    Returns dict with updated: repetitions, easiness, interval, next_review_date
    """

    if quality < 3:
        # Failed recall — reset
        repetitions = 0
        interval = 1
    else:
        # Successful recall — calculate new interval
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * easiness)
        repetitions += 1

    # Update easiness factor
    easiness = easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    easiness = max(easiness, MIN_EASINESS)

    # Calculate next review date
    from datetime import date, timedelta
    next_review = date.today() + timedelta(days=interval)

    return {
        "repetitions": repetitions,
        "easiness": round(easiness, 4),
        "interval": interval,
        "next_review_date": next_review.isoformat()
    }

def quality_label(quality: int) -> str:
    labels = {
        0: "Complete blackout",
        1: "Wrong but familiar",
        2: "Wrong but easy to recall",
        3: "Correct with difficulty",
        4: "Correct with hesitation",
        5: "Perfect recall"
    }
    return labels.get(quality, "Unknown")
