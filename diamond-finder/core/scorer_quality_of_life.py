"""
Quality of Life Scoring System

Scores apartments based on how incredible they are to LIVE IN.
Not about price, status, or investment - about daily experience.
"""
from typing import Dict
from .models import Diamond


class QualityOfLifeScorer:
    """
    Scores diamonds based on living experience quality.

    Key factors:
    - Tenure (people stayed because it's amazing)
    - Light quality (morning sun, no glare)
    - Views (not just "has views" but WHAT you see)
    - Space quality (ceiling height, proportions, layout)
    - Quiet (thick walls, location, insulation)
    - Unique features that enhance daily life
    - Social proof from people who lived there
    """

    def score(self, diamond: Diamond) -> float:
        """
        Score apartment quality of life (0-100+)

        Breakdown:
        - Long tenure: 0-30 points (strongest signal)
        - Social proof: 0-25 points (Reddit mentions, testimonials)
        - Building reputation: 0-15 points (recommend, loved living here)
        - Light quality: 0-15 points (morning sun, corner, exposures)
        - Views: 0-15 points (park, water, unobstructed)
        - Space quality: 0-15 points (high ceilings, layout, pre-war)
        - Outdoor space: 0-15 points (terrace, balcony, garden)
        - Unique experience: 0-15 points (duplex, private elevator)
        - Lived experience: 0-12 points (loved, amazing, perfect)
        - Quiet: 0-10 points (thick walls, peaceful)
        - Photo evidence: 0-10 points (visual proof of quality)
        """
        score = 0.0
        breakdown = {}

        why_text = ' '.join(diamond.why_special).lower()

        # TENURE - Strongest signal (0-30 points)
        if diamond.tenure_years:
            if diamond.tenure_years >= 40:
                tenure_score = 30  # 40+ years = genuinely extraordinary
            elif diamond.tenure_years >= 30:
                tenure_score = 25
            elif diamond.tenure_years >= 20:
                tenure_score = 20
            elif diamond.tenure_years >= 15:
                tenure_score = 15
            elif diamond.tenure_years >= 10:
                tenure_score = 10
            else:
                tenure_score = 5

            score += tenure_score
            breakdown['long_tenure'] = tenure_score

        # LIGHT QUALITY (0-15 points)
        light_score = 0

        light_keywords = {
            'south': 5,  # Best light
            'southeast corner': 10,  # Morning sun + afternoon sun
            'east': 5,  # Morning light
            'corner': 5,  # Multiple exposures
            'morning sun': 5,
            'bright': 3,
            'windows': 2,
            'natural light': 4,
            'skylight': 4,
        }

        for keyword, points in light_keywords.items():
            if keyword in why_text:
                light_score += points

        light_score = min(light_score, 15)
        score += light_score
        if light_score > 0:
            breakdown['light_quality'] = light_score

        # VIEWS (0-15 points)
        view_score = 0

        view_keywords = {
            'central park view': 10,
            'park view': 8,
            'water view': 8,
            'river view': 8,
            'hudson': 7,
            'east river': 7,
            'unobstructed': 6,
            'skyline': 5,
            'open view': 5,
            'protected view': 10,  # View won't be blocked
        }

        for keyword, points in view_keywords.items():
            if keyword in why_text:
                view_score += points

        view_score = min(view_score, 15)
        score += view_score
        if view_score > 0:
            breakdown['views'] = view_score

        # SPACE QUALITY (0-15 points)
        space_score = 0

        space_keywords = {
            'high ceiling': 6,
            '14 ft': 8,
            '12 ft': 6,
            'ceiling height': 4,
            'loft': 6,
            'open': 3,
            'proportions': 5,
            'layout': 3,
            'flow': 3,
            'original details': 5,
            'pre-war': 4,
            'thick walls': 6,  # Quiet + solid feeling
        }

        for keyword, points in space_keywords.items():
            if keyword in why_text:
                space_score += points

        space_score = min(space_score, 15)
        score += space_score
        if space_score > 0:
            breakdown['space_quality'] = space_score

        # OUTDOOR SPACE (0-15 points)
        outdoor_score = 0

        outdoor_keywords = {
            'terrace': 10,
            'private terrace': 12,
            'balcony': 6,
            'outdoor': 5,
            'roof access': 8,
            'private outdoor': 10,
            'garden': 8,
        }

        for keyword, points in outdoor_keywords.items():
            if keyword in why_text:
                outdoor_score += points

        outdoor_score = min(outdoor_score, 15)
        score += outdoor_score
        if outdoor_score > 0:
            breakdown['outdoor_space'] = outdoor_score

        # UNIQUE LIVING EXPERIENCE (0-15 points)
        unique_score = 0

        unique_keywords = {
            'through-floor': 10,
            'duplex': 8,
            'triplex': 10,
            'private elevator': 8,
            'only': 6,  # "only 3 like this"
            'rare': 5,
            'unique': 5,
            'one-of-a-kind': 8,
        }

        for keyword, points in unique_keywords.items():
            if keyword in why_text:
                unique_score += points

        unique_score = min(unique_score, 15)
        score += unique_score
        if unique_score > 0:
            breakdown['unique_experience'] = unique_score

        # QUIET / PEACE (0-10 points)
        quiet_score = 0

        quiet_keywords = {
            'quiet': 5,
            'peaceful': 5,
            'thick walls': 5,
            'soundproof': 6,
            'back of building': 4,  # Quieter than street
            'courtyard': 4,
            'no noise': 5,
        }

        for keyword, points in quiet_keywords.items():
            if keyword in why_text:
                quiet_score += points

        quiet_score = min(quiet_score, 10)
        score += quiet_score
        if quiet_score > 0:
            breakdown['quiet'] = quiet_score

        # SOCIAL PROOF (0-25 points) - BOOSTED for testimonial value
        if diamond.social_mentions > 0:
            # Scale: 1-2 mentions = 5-10pts, 5 mentions = 15pts, 10+ mentions = 20-25pts
            if diamond.social_mentions >= 10:
                social_score = 25
            elif diamond.social_mentions >= 8:
                social_score = 22
            elif diamond.social_mentions >= 5:
                social_score = 18
            elif diamond.social_mentions >= 3:
                social_score = 12
            else:
                social_score = diamond.social_mentions * 5

            score += social_score
            breakdown['social_proof'] = social_score

        # BUILDING REPUTATION (0-15 points)
        reputation_score = 0

        reputation_keywords = {
            'reddit': 2,  # Found via Reddit testimonials
            'mention': 2,  # Multiple mentions
            'recommend': 5,  # People recommend it
            'loved living': 8,  # Strong testimonial
            'best building': 8,
            'favorite': 6,
            'highly recommend': 7,
            'lived here': 4,
            'happy here': 5,
        }

        for keyword, points in reputation_keywords.items():
            if keyword in why_text:
                reputation_score += points

        reputation_score = min(reputation_score, 15)
        score += reputation_score
        if reputation_score > 0:
            breakdown['building_reputation'] = reputation_score

        # BUILDING QUALITY / MAINTENANCE (0-20 points)
        maintenance_score = 0

        if 'zero hpd violations' in why_text or '0 hpd violations' in why_text:
            maintenance_score = 20  # Extremely rare, excellent sign
        elif 'hpd violations' in why_text:
            # Has some violations mentioned, give partial credit for transparency
            if '1 hpd' in why_text or '2 hpd' in why_text:
                maintenance_score = 15
            elif '3 hpd' in why_text or '4 hpd' in why_text or '5 hpd' in why_text:
                maintenance_score = 10

        maintenance_keywords = {
            'well-maintained': 10,
            'excellent maintenance': 12,
            'responsive management': 8,
            'clean': 3,
            'pristine': 8,
        }

        for keyword, points in maintenance_keywords.items():
            if keyword in why_text:
                maintenance_score += points

        maintenance_score = min(maintenance_score, 20)
        score += maintenance_score
        if maintenance_score > 0:
            breakdown['building_maintenance'] = maintenance_score

        # Bonus for "loved living there" language
        love_keywords = ['loved', 'incredible', 'amazing', 'perfect', 'dream', 'never want to leave']
        love_count = sum(1 for kw in love_keywords if kw in why_text)
        if love_count > 0:
            love_score = min(love_count * 3, 12)
            score += love_score
            breakdown['lived_experience'] = love_score

        # Photos (evidence of quality, 0-10 points)
        if len(diamond.photos) > 0:
            photo_score = min(len(diamond.photos) / 5, 10)
            score += photo_score
            breakdown['photo_evidence'] = photo_score

        diamond.score = min(score, 100)
        diamond.score_breakdown = breakdown

        return diamond.score


def score_diamond_qol(diamond: Diamond) -> Diamond:
    """Score a diamond based on quality of life"""
    scorer = QualityOfLifeScorer()
    scorer.score(diamond)
    return diamond
