from datetime import datetime, timedelta, timezone
import unittest

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app
from app.models import Product, Timeslot


class TradeInFlowTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        SQLModel.metadata.create_all(self.engine)
        with Session(self.engine) as session:
            session.add(Product(name="Sofa bed", category="sofa", price=8900, stock=1))
            session.add(Timeslot(datetime=datetime.now(timezone.utc) + timedelta(days=1), technician_name="Test"))
            session.commit()

        def session_override():
            with Session(self.engine) as session:
                yield session

        app.dependency_overrides[get_session] = session_override
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()

    def test_profile_assessment_and_booking_persist_across_requests(self):
        registration = {"username": "qa_test", "password": "test-password", "email": "qa@example.test", "full_name": "QA Account"}
        self.assertEqual(self.client.post("/api/register", json=registration).status_code, 201)
        login = self.client.post("/api/login", json={"username": registration["username"], "password": registration["password"]})
        self.assertEqual(login.status_code, 200)
        headers = {"Authorization": "Bearer " + login.json()["access_token"]}
        self.assertEqual(self.client.get("/api/me", headers=headers).json()["full_name"], registration["full_name"])

        item = self.client.post("/api/items", headers=headers, json={"furniture_type": "sofa", "condition": "good"})
        self.assertEqual(item.status_code, 201)
        self.assertEqual(item.json()["estimated_price"], 1500)
        item_id = item.json()["id"]
        self.assertEqual(self.client.get(f"/api/items/{item_id}", headers=headers).json()["id"], item_id)
        self.assertEqual(self.client.get("/api/items", headers=headers).json()[0]["id"], item_id)

        booking = self.client.post("/api/bookings", headers=headers, json={"item_id": item_id, "product_id": 1, "timeslot_id": 1, "address": "test address"})
        self.assertEqual(booking.status_code, 201, booking.text)
        self.assertEqual(booking.json()["total_price"], 7400)


if __name__ == "__main__":
    unittest.main()
