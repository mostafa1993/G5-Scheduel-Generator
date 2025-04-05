"""
Schedule module for the G5 Spaced Repetition Schedule Generator.
"""

import json
from datetime import datetime, timedelta
import pandas as pd

from g5.models.set import Set


class G5Schedule:
    """
    Class for managing a G5 spaced repetition schedule.

    Handles creation, storage, and formatting of the schedule.
    """

    def __init__(self, start_date):
        """
        Initialize a new G5 schedule.

        Args:
          start_date: Datetime object of when to start the schedule
        """
        self.start_date = start_date
        self.sets = []

    def add_new_sets(self, new_sets_count, starting_set_number=1):
        """
        Add new sets to the schedule.

        Args:
          new_sets_count: Number of new sets to add
          starting_set_number: The set number to start with (default is 1)
        """
        # Create new sets
        for i in range(new_sets_count):
            set_index = starting_set_number + i
            set_name = f"Set {set_index:02d}"
            learn_date = self.start_date + timedelta(days=i)

            self.sets.append(Set(set_name, learn_date))

    def get_events_by_date(self):
        """
        Organize all events by date.

        Returns:
          Dictionary mapping dates to sets of activities
        """
        events_by_date = {}

        # Process all events for all sets
        for set_obj in self.sets:
            for event in set_obj.get_all_events():
                date = event["date"]
                date_str = date.strftime("%Y-%m-%d")

                if date_str not in events_by_date:
                    events_by_date[date_str] = {"New Words": None, "Reviews": []}

                if event["action_type"] == "learn":
                    events_by_date[date_str]["New Words"] = event["set_name"]
                else:
                    review_text = f"{event['set_name']} (R{event['review_number']})"
                    events_by_date[date_str]["Reviews"].append(review_text)

        return events_by_date

    def get_activity_list(self):
        """Get a flat list of all activities for JSON storage."""
        activities = []

        for set_obj in self.sets:
            # Add learning event
            learning = set_obj.get_learning_event()
            activities.append(
                {
                    "Date": learning["date"].strftime("%Y-%m-%d"),
                    "Action": f"Learn {learning['set_name']}",
                }
            )

            # Add review events
            for review in set_obj.get_review_events():
                activities.append(
                    {
                        "Date": review["date"].strftime("%Y-%m-%d"),
                        "Action": f"Review {review['set_name']} (R{review['review_number']})",
                    }
                )

        return activities

    def to_dataframe(self, day_offset=0):
        """
        Convert the schedule to a DataFrame for display.

        Args:
          day_offset: Offset for day numbering (for continuity in set sequences)

        Returns:
          Pandas DataFrame with one row per day
        """
        # Get events organized by date
        events_by_date = self.get_events_by_date()

        # Prepare rows for DataFrame
        display_rows = []

        for date_str, activities in sorted(events_by_date.items()):
            # Calculate day number with offset
            date = datetime.strptime(date_str, "%Y-%m-%d")
            day_number = (date - self.start_date).days + 1 + day_offset

            # Format date like "Apr 07 (D1)"
            formatted_date = f"{date.strftime('%b %d')} (D{day_number})"

            # Format reviews as comma-separated string
            reviews = ", ".join(activities["Reviews"]) if activities["Reviews"] else "-"

            display_rows.append(
                {
                    "Date": formatted_date,
                    "New Words": (
                        activities["New Words"] if activities["New Words"] else "-"
                    ),
                    "Reviews": reviews,
                }
            )

        return pd.DataFrame(display_rows)

    def to_dict(self):
        """Convert the schedule to a dictionary for JSON storage."""
        return {
            "sets": [set_obj.to_dict() for set_obj in self.sets],
            "start_date": self.start_date.strftime("%Y-%m-%d"),
            "full_schedule": self.get_activity_list(),
        }

    def save_to_json(self, json_path):
        """Save the schedule to a JSON file."""
        with open(json_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def export_to_ical(self, output_file):
        """
        Export the schedule to iCalendar format.

        Args:
          output_file: Path to save the .ics file
        """
        activities = self.get_activity_list()

        from g5.utils.icalendar_export import export_to_ical

        return export_to_ical(activities, output_file)
