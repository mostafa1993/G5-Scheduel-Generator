"""
iCalendar export utility for the G5 Spaced Repetition Schedule Generator.
"""

from datetime import datetime, timedelta
import uuid


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
