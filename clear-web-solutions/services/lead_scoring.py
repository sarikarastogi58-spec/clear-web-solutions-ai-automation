def score_lead_metadata(rating: str | None, review_count: int | None, website: str | None) -> dict:
    score = 40
    website_need_score = 50
    business_potential = 50

    if rating:
        try:
            numeric = float(rating)
            score += int((numeric - 3.5) * 15)
            business_potential += int((numeric - 3.5) * 10)
        except ValueError:
            pass

    if review_count:
        if review_count >= 100:
            score += 20
            business_potential += 15
        elif review_count >= 50:
            score += 10
            business_potential += 5

    if website:
        website_need_score = max(0, 50 - 20)
        score -= 10
    else:
        website_need_score = min(100, 80)
        score += 10

    score = max(0, min(100, score))
    website_need_score = max(0, min(100, website_need_score))
    business_potential = max(0, min(100, business_potential))

    if score >= 80:
        priority = "high"
    elif score >= 60:
        priority = "medium"
    else:
        priority = "low"

    return {
        "score": score,
        "website_need_score": website_need_score,
        "business_potential": business_potential,
        "priority": priority,
        "digital_gaps": "Improve local SEO, bookings, WhatsApp integration, and a mobile-friendly website.",
        "pitch_angle": "High review volume with a missing or weak website. Offer a restaurant website + WhatsApp booking package to capture more local customers.",
    }
