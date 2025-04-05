import json
import argparse
from datetime import datetime, timedelta
import pandas as pd
import uuid


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

        return export_to_ical(activities, output_file)


def export_to_ical(schedule, output_file):
    """
    Export schedule to iCalendar (.ics) format for import into Google Calendar.

    Args:
      schedule: List of activities from the full_schedule property
      output_file: Path to save the .ics file

    Returns:
      True if successful, False otherwise
    """
    try:
        from icalendar import Calendar, Event

        # Create calendar
        cal = Calendar()

        # Required properties for iCalendar files
        cal.add("prodid", "-//G5 Schedule Generator//g5_generator.py//EN")
        cal.add("version", "2.0")

        # Add calendar items - each activity as a separate event
        for activity in schedule:
            date_str = activity["Date"]
            action = activity["Action"]

            # Parse the date
            date = datetime.strptime(date_str, "%Y-%m-%d")

            # Create an event (instead of a todo item)
            event = Event()

            # Set summary (title)
            event.add("summary", action)

            # Set date - all-day event
            event.add("dtstart", date.date())
            event.add("dtend", date.date() + timedelta(days=1))  # End of the day

            # Add emoji to the summary based on action type
            if "Learn" in action:
                event.add("summary", f"📚 {action}")  # Book emoji for learning
                event.add("color", "9")  # Blue
            elif "(R1)" in action:
                event.add("summary", f"🔍 {action}")  # First review
                event.add("color", "5")  # Yellow
            elif "(R2)" in action:
                event.add("summary", f"🔄 {action}")  # Second review
                event.add("color", "5")  # Yellow
            elif "(R3)" in action:
                event.add("summary", f"📝 {action}")  # Third review
                event.add("color", "7")  # Orange
            elif "(R4)" in action:
                event.add("summary", f"✅ {action}")  # Fourth review
                event.add("color", "11")  # Red

            # Add a description
            event.add("description", f"G5 Spaced Repetition - {action}")

            # Add a unique identifier
            event.add("uid", str(uuid.uuid4()))

            # Add the event to the calendar
            cal.add_component(event)

        # Write to file
        with open(output_file, "wb") as f:
            f.write(cal.to_ical())

        return True

    except ImportError:
        print("Could not create iCalendar file: icalendar package not installed")
        print("Install with: pip install icalendar")
        return False
    except Exception as e:
        print(f"Error creating iCalendar file: {e}")
        return False


def generate_g5_schedule(
    start_date_str,
    new_sets,
    set_number=1,
    json_path="g5_schedule.json",
    return_schedule=False,
):
    """
    Generate a G5 review schedule for spaced repetition learning.

    Args:
      start_date_str: String date in format 'DD-MM-YYYY' to start the schedule
      new_sets: Number of new sets to add to the schedule
      set_number: The set number that corresponds to start_date (default: 1 for first set)
      json_path: Path to JSON file for storing schedule data
      return_schedule: Whether to return the G5Schedule object in addition to DataFrame

    Returns:
      If return_schedule is False: DataFrame containing the complete schedule
      If return_schedule is True: (DataFrame, G5Schedule) tuple
    """
    try:
        # Convert start date from string to datetime
        given_date = datetime.strptime(start_date_str, "%d-%m-%Y")

        # Validate input
        if new_sets <= 0:
            raise ValueError("Number of new sets must be positive")

        if set_number < 1:
            raise ValueError("Set number must be positive")

        # Create schedule object directly from the given date and set number
        schedule = G5Schedule(given_date)

        # Add only the requested sets with the correct set numbers
        schedule.add_new_sets(new_sets, set_number)

        # Save to JSON
        schedule.save_to_json(json_path)

        # Calculate the theoretical day number for display
        # If this is set 1, day 1 is fine. Otherwise we need to offset
        day_offset = set_number - 1  # Each set is 1 day apart

        # Get DataFrame with the correct offset for day numbers
        df = schedule.to_dataframe(day_offset)

        # Return appropriate result based on return_schedule parameter
        if return_schedule:
            return df, schedule, None, set_number
        else:
            return df

    except Exception as e:
        print(f"Error generating schedule: {e}")
        raise


def main():
    """Command line interface for the G5 schedule generator."""
    parser = argparse.ArgumentParser(
        description="Generate a G5 spaced repetition schedule"
    )
    parser.add_argument(
        "-d",
        "--start-date",
        type=str,
        help="Start date in DD-MM-YYYY format (defaults to today if not specified)",
        default=datetime.now().strftime("%d-%m-%Y"),
    )
    parser.add_argument(
        "-n", "--num-sets", type=int, required=True, help="Number of new sets to add"
    )
    parser.add_argument(
        "-s",
        "--set-number",
        type=int,
        default=1,
        help="Set number that corresponds to the start date (default: 1)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="g5_schedule.json",
        help="Path to output JSON file (default: g5_schedule.json)",
    )
    parser.add_argument(
        "-c",
        "--calendar",
        type=str,
        help="Export schedule to iCalendar (.ics) file for Google Calendar import",
    )

    args = parser.parse_args()

    try:
        # Generate the schedule
        df, schedule, _, _ = generate_g5_schedule(
            start_date_str=args.start_date,
            new_sets=args.num_sets,
            set_number=args.set_number,
            json_path=args.output,
            return_schedule=True,
        )

        # Display the schedule
        print(f"\nG5 Schedule (saved to {args.output}):")
        print(f"Starting with Set {args.set_number:02d} on {args.start_date}")
        pd.set_option("display.max_colwidth", 100)
        print(df.to_string(index=False))

        # Export to iCalendar if requested
        if args.calendar:
            # Add .ics extension if not provided
            calendar_path = args.calendar
            if not calendar_path.lower().endswith(".ics"):
                calendar_path = f"{calendar_path}.ics"

            # Export calendar
            if schedule.export_to_ical(calendar_path):
                print(f"Schedule exported to iCalendar: {calendar_path}")
                print("You can import this file into Google Calendar:")
                print("1. Go to Google Calendar website")
                print("2. Click the '+' button next to 'Other calendars'")
                print("3. Select 'Import'")
                print("4. Upload the .ics file")

        return df

    except Exception as e:
        print(f"Failed to generate schedule: {e}")
        return None


if __name__ == "__main__":
    df = main()
