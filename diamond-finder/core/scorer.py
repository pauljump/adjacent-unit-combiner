"""
Scoring system for evaluating diamond candidates
"""
from typing import Dict
from .models import Diamond


class DiamondScorer:
    """Scores diamond candidates based on multiple signals"""

    def score(self, diamond: Diamond) -> float:
        """
        Calculate overall diamond score (0-100)

        Scoring breakdown:
        - Price premium: 0-25 points
        - Tenure: 0-25 points
        - Photos/evidence: 0-15 points
        - Social proof: 0-10 points
        - Scarcity signals: 0-25 points
        """
        score = 0.0
        breakdown = {}

        # Price premium signal (0-25 points)
        if diamond.price_premium_pct is not None:
            price_score = min(diamond.price_premium_pct / 2, 25)  # 50%+ premium = max points
            score += price_score
            breakdown['price_premium'] = price_score

        # Tenure signal (0-25 points)
        if diamond.tenure_years is not None:
            if diamond.tenure_years >= 20:
                tenure_score = 25
            elif diamond.tenure_years >= 15:
                tenure_score = 20
            elif diamond.tenure_years >= 10:
                tenure_score = 15
            elif diamond.tenure_years >= 5:
                tenure_score = 10
            else:
                tenure_score = 5
            score += tenure_score
            breakdown['tenure'] = tenure_score

        # Photo evidence signal (0-15 points)
        photo_count = len(diamond.photos)
        photo_score = min(photo_count / 2, 15)  # 30+ photos = max points
        score += photo_score
        breakdown['photos'] = photo_score

        # Floor plan bonus
        if diamond.floor_plan_url:
            score += 5
            breakdown['floor_plan'] = 5

        # Social proof signal (0-10 points)
        if diamond.social_mentions > 0:
            social_score = min(diamond.social_mentions * 2, 10)  # 5+ mentions = max points
            score += social_score
            breakdown['social_proof'] = social_score

        # Scarcity signals from why_special (0-35 points)
        scarcity_score = 0

        scarcity_keywords = {
            'corner': 5,
            'terrace': 8,
            'outdoor space': 8,
            'roof': 10,
            'private elevator': 10,
            'duplex': 8,
            'through-floor': 8,
            'combine': 10,
            'views': 5,
            'pre-war': 5,
            'original details': 5,
            'rare': 5,
            'only': 7,
            'unique': 5,
            'penthouse': 10,
            'landmark': 10,
            'historic': 8,
            'architectural significance': 10,
            'record': 12,
            'most expensive': 12,
            'sold for $': 8,
            'pritzker': 15,  # Pritzker Prize winning architect
            'robert a.m. stern': 10,
            'tadao ando': 10,
            '360-degree': 8,
            'central park': 7,
        }

        why_text = ' '.join(diamond.why_special).lower()
        for keyword, points in scarcity_keywords.items():
            if keyword in why_text:
                scarcity_score += points

        scarcity_score = min(scarcity_score, 35)
        score += scarcity_score
        breakdown['scarcity'] = scarcity_score

        # Multiple strategies found it (consensus bonus, 0-10 points)
        if len(diamond.found_by_strategies) > 1:
            consensus_score = min(len(diamond.found_by_strategies) * 2, 10)
            score += consensus_score
            breakdown['consensus'] = consensus_score

        diamond.score = min(score, 100)  # Cap at 100
        diamond.score_breakdown = breakdown

        return diamond.score


def score_diamond(diamond: Diamond) -> Diamond:
    """Convenience function to score a diamond"""
    scorer = DiamondScorer()
    scorer.score(diamond)
    return diamond
