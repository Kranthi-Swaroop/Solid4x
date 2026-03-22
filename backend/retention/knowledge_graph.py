from .database import get_mastery_stats

def build_student_knowledge_graph(profile_id: str) -> dict:
    """
    Constructs a visual representation or data map of a student's mastery across subjects.
    This aggregates database stats and formats them for the frontend heatmap.
    """
    db_stats = get_mastery_stats(profile_id)
    
    # Format into a clean structure for the frontend heatmap
    graph = {
        "overall_health": 0,
        "subjects": []
    }
    
    total_mastered = 0
    total_concepts = 0
    
    for subject, stats in db_stats.items():
        mastered = stats["mastered"]
        total = stats["total_concepts"]
        easiness = stats["avg_easiness"]
        
        total_mastered += mastered
        total_concepts += total
        
        # Calculate a 0-100 mastery score
        score = int((mastered / total * 100) if total > 0 else 0)
        
        graph["subjects"].append({
            "subject": subject,
            "mastery_score": score,
            "total_cards": total,
            "avg_easiness": easiness
        })
        
    if total_concepts > 0:
        graph["overall_health"] = int((total_mastered / total_concepts) * 100)
        
    # Sort subjects by lowest mastery first (to highlight weak areas)
    graph["subjects"].sort(key=lambda x: x["mastery_score"])
    
    return graph
