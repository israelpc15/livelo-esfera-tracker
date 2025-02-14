import datetime
from typing import List, Optional, Dict, Any

class WatchStore:
    """
    Represents a watch store item from watchstoreslist.json.
    """
    def __init__(self, code: str, name: str, valid_until: str, min_points: int, categories: Optional[List[str]] = None) -> None:
        """
        Initializes a WatchStore instance.

        Args:
            code (str): The store code.
            name (str): The store name.
            valid_until (str): Expiration date in 'YYYY-MM-DD' format.
            min_points (int): Minimum desired points.
            categories (Optional[List[str]]): List of categories (optional).
        """
        self.code = code
        self.name = name
        # Parse valid_until into a date object
        self.valid_until = datetime.datetime.strptime(valid_until, '%Y-%m-%d').date() if valid_until else None
        self.min_points = min_points
        self.categories = categories or []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WatchStore":
        """
        Creates a WatchStore instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary with keys corresponding to the JSON item.

        Returns:
            WatchStore: The created WatchStore instance.
        """
        return cls(
            code=data.get("code"),
            name=data.get("name"),
            valid_until=data.get("valid_until"),
            min_points=data.get("min_points"),
            categories=data.get("categories")
        )

    def is_valid(self) -> bool:
        """
        Checks if the store is still valid (i.e., the valid_until date has not passed).

        Returns:
            bool: True if valid, False otherwise.
        """
        if self.valid_until is None:
            return False
        return self.valid_until >= datetime.date.today()

    def __repr__(self) -> str:
        """
        Returns a string representation of the WatchStore instance.
        """
        return (f"WatchStore(code='{self.code}', name='{self.name}', "
                f"valid_until='{self.valid_until}', min_points={self.min_points}, "
                f"categories={self.categories})")
