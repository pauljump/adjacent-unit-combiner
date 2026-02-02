"""
Base class for all search strategies
"""
from abc import ABC, abstractmethod
from typing import List
from .models import Diamond


class SearchStrategy(ABC):
    """Base class that all search strategies inherit from"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def search(self) -> List[Diamond]:
        """
        Execute the search strategy.

        Returns:
            List of Diamond candidates found by this strategy
        """
        pass

    def _create_diamond(
        self,
        address: str,
        unit: str,
        listing_type: str = "sale",
        price: float = None,
        bedrooms: int = None,
        sqft: float = None,
        why_special: List[str] = None,
        **kwargs
    ) -> Diamond:
        """
        Helper method to create a Diamond with this strategy tagged

        Args:
            address: Building address
            unit: Unit number
            listing_type: "sale" or "rental"
            price: Listing price
            bedrooms: Number of bedrooms
            sqft: Square footage
            why_special: List of reasons why this is special
            **kwargs: Additional Diamond fields

        Returns:
            Diamond object with this strategy in found_by_strategies
        """
        diamond = Diamond(
            address=address,
            unit=unit,
            listing_type=listing_type,
            price=price,
            bedrooms=bedrooms,
            sqft=sqft,
            why_special=why_special or [],
            found_by_strategies=[self.name],
            **kwargs
        )
        return diamond

    def __repr__(self):
        return f"SearchStrategy(name='{self.name}')"
