"""
Daily briefing generator - the core value proposition
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from .database import SessionLocal
from .config import get_settings
from .logging_config import get_logger
from ..models.database_models import (
    Student, Schedule, ClassRoster, QuickLog, Reminder, DutyRota,
    Communication, Assessment
)

logger = get_logger("briefing")
settings = get_settings()


class DailyBriefing:
    """Daily briefing data structure"""

    def __init__(self, briefing_date: date = None):
        self.date = briefing_date or date.today()
        self.day_name = self.date.strftime("%A")

        # Core briefing sections
        self.schedule: List[Dict] = []
        self.student_alerts: Dict[str, List[Dict]] = {}
        self.duty_assignments: List[Dict] = []
        self.reminders: List[Dict] = []
        self.communications: List[Dict] = []
        self.insights: List[str] = []

        # Metadata
        self.generated_at = datetime.now()
        self.total_students = 0
        self.classes_today = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            "date": self.date.isoformat(),
            "day_name": self.day_name,
            "schedule": self.schedule,
            "student_alerts": self.student_alerts,
            "duty_assignments": self.duty_assignments,
            "reminders": self.reminders,
            "communications": self.communications,
            "insights": self.insights,
            "metadata": {
                "generated_at": self.generated_at.isoformat(),
                "total_students": self.total_students,
                "classes_today": self.classes_today
            }
        }


class BriefingEngine:
    """Generates daily briefings"""

    def __init__(self):
        self.settings = get_settings()

    def generate_briefing(self, briefing_date: date = None) -> DailyBriefing:
        """Generate complete daily briefing"""
        briefing = DailyBriefing(briefing_date)

        db = SessionLocal()
        try:
            # Generate each section
            self._add_schedule(db, briefing)
            self._add_student_alerts(db, briefing)
            self._add_duty_assignments(db, briefing)
            self._add_reminders(db, briefing)
            self._add_communications(db, briefing)
            self._add_insights(db, briefing)

            logger.info(f"Generated briefing for {briefing.date}")
            return briefing

        finally:
            db.close()

    def _add_schedule(self, db: Session, briefing: DailyBriefing):
        """Add today's schedule with class details"""
        # Get today's schedule
        today_schedule = db.query(Schedule).filter(
            Schedule.day_of_week == briefing.day_name
        ).order_by(Schedule.period).all()

        if not today_schedule:
            briefing.schedule = []
            return

        briefing.classes_today = len(today_schedule)

        for entry in today_schedule:
            # Get students in this class
            class_students = db.query(Student).join(ClassRoster).filter(
                ClassRoster.class_code == entry.class_code
            ).all()

            briefing.total_students += len(class_students)

            # Get recent logs for this class (last 2 weeks)
            two_weeks_ago = datetime.now() - timedelta(days=14)
            recent_logs = db.query(QuickLog).filter(
                and_(
                    QuickLog.class_code == entry.class_code,
                    QuickLog.timestamp >= two_weeks_ago
                )
            ).order_by(desc(QuickLog.timestamp)).limit(10).all()

            # Count high support students
            high_support_count = sum(1 for s in class_students if s.support_level >= 2)

            schedule_entry = {
                "period": entry.period,
                "start_time": entry.start_time,
                "end_time": entry.end_time,
                "class_code": entry.class_code,
                "subject": entry.subject,
                "room": entry.room,
                "student_count": len(class_students),
                "high_support_count": high_support_count,
                "recent_incidents": len([log for log in recent_logs if log.log_type == "negative"])
            }

            briefing.schedule.append(schedule_entry)

    def _add_student_alerts(self, db: Session, briefing: DailyBriefing):
        """Add student alerts for each class"""
        for schedule_entry in briefing.schedule:
            class_code = schedule_entry["class_code"]

            # Get students in this class
            class_students = db.query(Student).join(ClassRoster).filter(
                ClassRoster.class_code == class_code
            ).all()

            alerts = []

            for student in class_students:
                student_alerts = []

                # Check support level
                if student.support_level >= 2:
                    student_alerts.append({
                        "type": "high_support",
                        "level": student.support_level,
                        "notes": student.support_notes or "High support needs"
                    })

                # Check recent negative logs (last 3 days)
                three_days_ago = datetime.now() - timedelta(days=3)
                recent_negative_logs = db.query(QuickLog).filter(
                    and_(
                        QuickLog.student_id == student.id,
                        QuickLog.log_type == "negative",
                        QuickLog.timestamp >= three_days_ago
                    )
                ).count()

                if recent_negative_logs >= 2:
                    student_alerts.append({
                        "type": "behavior_pattern",
                        "count": recent_negative_logs,
                        "recent": True
                    })

                # Check for no positive logs in 2 weeks
                two_weeks_ago = datetime.now() - timedelta(days=14)
                positive_logs = db.query(QuickLog).filter(
                    and_(
                        QuickLog.student_id == student.id,
                        QuickLog.log_type == "positive",
                        QuickLog.timestamp >= two_weeks_ago
                    )
                ).count()

                if positive_logs == 0:
                    student_alerts.append({
                        "type": "no_positive_interaction",
                        "days": 14
                    })

                if student_alerts:
                    alerts.append({
                        "student_id": student.id,
                        "student_name": student.name,
                        "alerts": student_alerts
                    })

            if alerts:
                briefing.student_alerts[class_code] = alerts

    def _add_duty_assignments(self, db: Session, briefing: DailyBriefing):
        """Add today's duty assignments"""
        today_duties = db.query(DutyRota).filter(
            DutyRota.date == briefing.date
        ).order_by(DutyRota.start_time).all()

        for duty in today_duties:
            briefing.duty_assignments.append({
                "duty_type": duty.duty_type,
                "location": duty.location,
                "start_time": duty.start_time,
                "end_time": duty.end_time,
                "notes": duty.notes
            })

    def _add_reminders(self, db: Session, briefing: DailyBriefing):
        """Add active reminders"""
        # Daily reminders
        daily_reminders = db.query(Reminder).filter(
            and_(
                Reminder.active == True,
                Reminder.reminder_type == "daily"
            )
        ).all()

        # Weekly reminders for today
        weekly_reminders = db.query(Reminder).filter(
            and_(
                Reminder.active == True,
                Reminder.reminder_type == "weekly",
                Reminder.days.contains(briefing.day_name)
            )
        ).all()

        # One-time reminders for today
        today_str = briefing.date.isoformat()
        once_reminders = db.query(Reminder).filter(
            and_(
                Reminder.active == True,
                Reminder.reminder_type == "once"
            )
        ).all()

        all_reminders = daily_reminders + weekly_reminders + once_reminders

        for reminder in all_reminders:
            # Check if this reminder should trigger today
            should_trigger = self._should_trigger_reminder(reminder, briefing)
            if should_trigger:
                briefing.reminders.append({
                    "title": reminder.title,
                    "message": reminder.message,
                    "trigger_time": reminder.trigger_time,
                    "type": reminder.reminder_type
                })

    def _add_communications(self, db: Session, briefing: DailyBriefing):
        """Add unread communications"""
        # Get recent unread communications (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        unread_comms = db.query(Communication).filter(
            and_(
                Communication.read == False,
                Communication.received_date >= week_ago
            )
        ).order_by(desc(Communication.received_date)).limit(10).all()

        for comm in unread_comms:
            briefing.communications.append({
                "id": comm.id,
                "subject": comm.subject,
                "sender": comm.sender,
                "category": comm.category,
                "campus": comm.campus,
                "received_date": comm.received_date.isoformat(),
                "action_required": comm.action_required,
                "urgent": comm.category == "urgent"
            })

    def _add_insights(self, db: Session, briefing: DailyBriefing):
        """Add AI-generated insights"""
        insights = []

        # Class engagement insights
        for class_code, alerts in briefing.student_alerts.items():
            high_support_count = len([a for a in alerts if any(alert.get("type") == "high_support" for alert in a["alerts"])])
            behavior_issues = len([a for a in alerts if any(alert.get("type") == "behavior_pattern" for alert in a["alerts"])])

            if high_support_count > 0:
                insights.append(f"Class {class_code}: {high_support_count} high-support students need attention")

            if behavior_issues > 0:
                insights.append(f"Class {class_code}: {behavior_issues} students showing behavior patterns")

        # Overall insights
        if briefing.total_students > 0:
            alert_percentage = (sum(len(alerts) for alerts in briefing.student_alerts.values()) / briefing.total_students) * 100
            if alert_percentage > 20:
                insights.append(f"High alert rate today: {alert_percentage:.1f}% of students need attention")

        briefing.insights = insights[:5]  # Limit to top 5 insights

    def _should_trigger_reminder(self, reminder: Reminder, briefing: DailyBriefing) -> bool:
        """Check if a reminder should trigger today"""
        if reminder.reminder_type == "daily":
            return True
        elif reminder.reminder_type == "weekly":
            return briefing.day_name in (reminder.days or "")
        elif reminder.reminder_type == "once":
            # For once reminders, check if it's due today
            # This is a simplified check - in reality you'd want more sophisticated logic
            return True
        return False


def generate_daily_briefing(briefing_date: date = None) -> DailyBriefing:
    """Convenience function to generate briefing"""
    engine = BriefingEngine()
    return engine.generate_briefing(briefing_date)


def format_briefing_text(briefing: DailyBriefing) -> str:
    """Format briefing as readable text"""
    lines = []
    lines.append("=" * 60)
    lines.append(f"Date: {briefing.day_name.upper()}, {briefing.date}")
    lines.append("=" * 60)

    # Schedule
    if briefing.schedule:
        lines.append("\nTODAY'S SCHEDULE")
        lines.append("-" * 40)
        for entry in briefing.schedule:
            alerts = []
            if entry["high_support_count"] > 0:
                alerts.append(f"ALERT: {entry['high_support_count']} high-support")
            if entry["recent_incidents"] > 0:
                alerts.append(f"WARNING: {entry['recent_incidents']} incidents")

            alert_text = f" ({', '.join(alerts)})" if alerts else ""

            lines.append(
                f"{entry['start_time']}-{entry['end_time']} │ "
                f"{entry['class_code']} {entry['subject']} │ "
                f"Room {entry['room']} │ "
                f"{entry['student_count']} students{alert_text}"
            )

    # Student alerts
    if briefing.student_alerts:
        lines.append("\nSTUDENT ALERTS")
        lines.append("-" * 40)
        for class_code, alerts in briefing.student_alerts.items():
            lines.append(f"\n{class_code}:")
            for alert in alerts:
                alert_types = [a["type"] for a in alert["alerts"]]
                lines.append(f"  • {alert['student_name']}: {', '.join(alert_types)}")

    # Duty assignments
    if briefing.duty_assignments:
        lines.append("\nDUTY ASSIGNMENTS")
        lines.append("-" * 40)
        for duty in briefing.duty_assignments:
            lines.append(
                f"• {duty['duty_type']}: {duty['location']} "
                f"({duty['start_time']}-{duty['end_time']})"
            )

    # Reminders
    if briefing.reminders:
        lines.append("\nREMINDERS")
        lines.append("-" * 40)
        for reminder in briefing.reminders:
            lines.append(f"• {reminder['title']}: {reminder['message']}")

    # Communications
    urgent_comms = [c for c in briefing.communications if c["urgent"]]
    if urgent_comms:
        lines.append("\nURGENT COMMUNICATIONS")
        lines.append("-" * 40)
        for comm in urgent_comms:
            lines.append(f"• {comm['subject']} ({comm['campus'] or 'Both'})")

    # Insights
    if briefing.insights:
        lines.append("\nINSIGHTS")
        lines.append("-" * 40)
        for insight in briefing.insights:
            lines.append(f"• {insight}")

    lines.append("\n" + "=" * 60)
    lines.append(f"Generated at {briefing.generated_at.strftime('%H:%M:%S')}")

    return "\n".join(lines)