"""
Set module for the G5 Spaced Repetition Schedule Generator.
"""

from datetime import datetime, timedelta


class Set:
    """
    Class representing a learning set in the G5 method.

    Each set has a name, learning date, and generates its own review schedule.
    """

    def __init__(self, name, learn_date):
        """
        Initialize a new learning set.

        Args:
          name: Name of the set (e.g., 'Set 01')
          learn_date: Datetime object of when this set is learned
        """
        self.name = name
        self.learn_date = learn_date
        self.review_days = [2, 4, 8, 15]  # Days when reviews happen (day 1 is learning)

    def get_learning_event(self):
        """Return the learning event for this set."""
        return {"date": self.learn_date, "action_type": "learn", "set_name": self.name}

    def get_review_events(self):
        """Generate all review events for this set."""
        review_events = []

        for i, days_offset in enumerate(self.review_days):
            review_date = self.learn_date + timedelta(
                days=days_offset - 1
            )  # -1 because day 1 is learning
            review_events.append(
                {
                    "date": review_date,
                    "action_type": "review",
                    "set_name": self.name,
                    "review_number": i + 1,
                }
            )

        return review_events

    def get_all_events(self):
        """Get all events (learning and reviews) for this set."""
        return [self.get_learning_event()] + self.get_review_events()

    def to_dict(self):
        """Convert the set to a dictionary for JSON storage."""
        return {
            "set": self.name,
            "learned_on": self.learn_date.strftime("%Y-%m-%d"),
            "review_days": [
                (self.learn_date + timedelta(days=day - 1)).strftime("%Y-%m-%d")
                for day in self.review_days
            ],
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Set object from dictionary data."""
        name = data["set"]
        learn_date = datetime.strptime(data["learned_on"], "%Y-%m-%d")
        return cls(name, learn_date)
