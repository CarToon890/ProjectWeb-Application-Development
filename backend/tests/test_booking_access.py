from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import unittest

from fastapi import HTTPException

from app.routers.bookings import (
    _fallback_future_timeslots,
    _require_access,
    _require_staff_assignment,
)


class BookingAccessTests(unittest.TestCase):
    def test_staff_can_access_only_assigned_booking(self):
        booking = SimpleNamespace(user_id=7)
        assigned_slot = SimpleNamespace(technician_name="ทีมช่าง A")
        staff = SimpleNamespace(id=2, role="staff", full_name="ทีมช่าง A")
        other_staff = SimpleNamespace(id=3, role="staff", full_name="ทีมช่าง B")

        _require_access(booking, staff, assigned_slot)
        with self.assertRaises(HTTPException) as error:
            _require_access(booking, other_staff, assigned_slot)
        self.assertEqual(error.exception.status_code, 403)

    def test_staff_cannot_update_unassigned_booking(self):
        slot = SimpleNamespace(technician_name="ทีมช่าง A")
        staff = SimpleNamespace(role="staff", full_name="ทีมช่าง B")

        with self.assertRaises(HTTPException) as error:
            _require_staff_assignment(slot, staff, "forbidden")
        self.assertEqual(error.exception.status_code, 403)

    def test_fallback_timeslot_filter_normalizes_utc_and_boolean_values(self):
        future_naive = datetime.utcnow() + timedelta(days=1)
        future_aware = datetime.now(timezone.utc) + timedelta(days=2)
        past = datetime.now(timezone.utc) - timedelta(days=1)
        slots = [
            SimpleNamespace(id=1, datetime=future_naive, is_available=True),
            SimpleNamespace(id=2, datetime=future_aware, is_available="true"),
            SimpleNamespace(id=3, datetime=past, is_available=True),
            SimpleNamespace(id=4, datetime=future_naive, is_available=False),
        ]

        session = SimpleNamespace(exec=lambda _query: SimpleNamespace(all=lambda: slots))

        result = _fallback_future_timeslots(session)
        self.assertEqual([slot.id for slot in result], [1, 2])


if __name__ == "__main__":
    unittest.main()
