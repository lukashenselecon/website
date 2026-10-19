import base64
import io
import os
import tempfile
import threading
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

from office_hours.app import connect_db, create_app, slot_end, upcoming_tuesdays
from office_hours.maintenance import remove_expired_bookings


MONDAY = datetime(2026, 10, 19, 12, 0, tzinfo=ZoneInfo("Asia/Shanghai"))


class BookingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db_path = str(Path(self.temp.name) / "bookings.sqlite3")
        self.uploads = str(Path(self.temp.name) / "uploads")
        self.app = create_app({
            "TESTING": True,
            "DATABASE": self.db_path,
            "UPLOAD_DIR": self.uploads,
            "SIGNING_KEY": "a-test-secret-key-longer-than-thirty-two-chars",
            "ADMIN_PASSWORD": "owner-test-password",
        })
        self.time_patch = patch("office_hours.app.now_beijing", return_value=MONDAY)
        self.time_patch.start()
        self.addCleanup(self.time_patch.stop)
        self.client = self.app.test_client()

    def enter(self, email="student@stu.pku.edu.cn"):
        response = self.client.post("/api/office-hours/start", json={"name": "Test Student", "email": email})
        self.assertEqual(response.status_code, 200)
        return response.json["token"]

    def book(self, token, date="2026-10-20", time="10:00", purpose="Discuss my thesis", attachments=None):
        data = {"token": token, "date": date, "time": time, "purpose": purpose}
        if attachments:
            data["attachments"] = attachments
        return self.client.post("/api/office-hours/book", data=data)

    def test_schedule_requires_name_and_pku_email(self):
        self.assertEqual(self.client.post("/api/office-hours/slots", json={}).status_code, 401)
        self.assertEqual(self.client.post("/api/office-hours/start", json={"name": "X", "email": "x@example.com"}).status_code, 400)
        self.assertEqual(self.client.post("/api/office-hours/start", json={"name": "Tester", "email": "x@pku.edu.cn.evil.com"}).status_code, 400)
        token = self.enter("student@gsm.pku.edu.cn")
        response = self.client.post("/api/office-hours/slots", json={"token": token})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["dates"]), 4)
        self.assertEqual(len(response.json["dates"][0]["slots"]), 7)

    def test_encoded_admin_password_from_deployment(self):
        password = "a private admin password with punctuation!"
        encoded = base64.b64encode(password.encode()).decode()
        with patch.dict(os.environ, {"OFFICE_HOURS_ADMIN_PASSWORD_B64": encoded}):
            deployed = create_app({
                "TESTING": True,
                "DATABASE": str(Path(self.temp.name) / "encoded.sqlite3"),
                "UPLOAD_DIR": self.uploads,
                "SIGNING_KEY": "a-test-secret-key-longer-than-thirty-two-chars",
            })
        credentials = base64.b64encode(f"lukas:{password}".encode()).decode()
        response = deployed.test_client().get(
            "/api/office-hours/admin/", headers={"Authorization": f"Basic {credentials}"})
        self.assertEqual(response.status_code, 200)

    def test_two_simultaneous_submissions_cannot_take_one_slot(self):
        token = self.enter()
        barrier = threading.Barrier(2)
        results = []

        def attempt():
            with self.app.test_client() as client:
                barrier.wait()
                response = client.post("/api/office-hours/book", data={
                    "token": token, "date": "2026-10-20", "time": "10:00",
                    "purpose": "Discuss my thesis"})
                results.append(response.status_code)

        workers = [threading.Thread(target=attempt) for _ in range(2)]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()
        self.assertEqual(sorted(results), [201, 409])
        with connect_db(self.db_path) as db:
            count = db.execute("SELECT COUNT(*) FROM bookings WHERE status='active'").fetchone()[0]
        self.assertEqual(count, 1)

    def test_cutoff_and_upload_are_enforced(self):
        token = self.enter()
        bad = self.book(token, attachments=[(io.BytesIO(b"not a pdf"), "notes.pdf")])
        self.assertEqual(bad.status_code, 400)
        ok = self.book(token, attachments=[(io.BytesIO(b"%PDF-1.4\nhello"), "notes.pdf")])
        self.assertEqual(ok.status_code, 201)
        with connect_db(self.db_path) as db:
            file = db.execute("SELECT * FROM uploads").fetchone()
        self.assertIsNotNone(file)
        self.assertTrue((Path(self.uploads) / file["stored_name"]).exists())
        self.assertEqual(self.client.get(f"/api/office-hours/admin/file/{file['id']}").status_code, 401)
        auth = {"Authorization": "Basic bHVrYXM6b3duZXItdGVzdC1wYXNzd29yZA=="}
        response = self.client.get(f"/api/office-hours/admin/file/{file['id']}", headers=auth)
        self.assertEqual(response.status_code, 200)
        response.close()
        with patch("office_hours.app.now_beijing", return_value=MONDAY.replace(hour=20, minute=1)):
            self.assertEqual(self.book(token, time="10:15").status_code, 409)

    def test_blocked_date_and_admin_auth(self):
        self.assertEqual(self.client.get("/api/office-hours/admin/").status_code, 401)
        auth = {"Authorization": "Basic bHVrYXM6b3duZXItdGVzdC1wYXNzd29yZA=="}
        page = self.client.get("/api/office-hours/admin/", headers=auth)
        self.assertEqual(page.status_code, 200)
        csrf = page.text.split('name="csrf" value="')[1].split('"')[0]
        block = self.client.post("/api/office-hours/admin/block", headers=auth,
                                 data={"date": "2026-10-20", "csrf": csrf})
        self.assertEqual(block.status_code, 303)
        token = self.enter()
        self.assertEqual(self.book(token).status_code, 409)

    def test_private_summary_lists_tuesday_bookings_and_requires_owner_login(self):
        token = self.enter()
        self.assertEqual(self.book(token, attachments=[(io.BytesIO(b"%PDF-1.4\nhello"), "notes.pdf")]).status_code, 201)
        url = "/api/office-hours/admin/summary?date=2026-10-20"
        self.assertEqual(self.client.get(url).status_code, 401)
        auth = {"Authorization": "Basic bHVrYXM6b3duZXItdGVzdC1wYXNzd29yZA=="}
        self.assertEqual(self.client.get(url.replace("2026-10-20", "2026-10-19"), headers=auth).status_code, 400)
        response = self.client.get(url, headers=auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["count"], 1)
        booking = response.json["bookings"][0]
        self.assertEqual((booking["time"], booking["end"]), ("10:00", "10:15"))
        self.assertEqual(booking["purpose"], "Discuss my thesis")
        self.assertEqual(booking["files"][0]["name"], "notes.pdf")

    def test_expired_booking_and_file_are_removed(self):
        token = self.enter()
        self.assertEqual(self.book(token, attachments=[(io.BytesIO(b"%PDF-1.4\nhello"), "notes.pdf")]).status_code, 201)
        with connect_db(self.db_path) as db:
            stored_name = db.execute("SELECT stored_name FROM uploads").fetchone()[0]
        self.assertEqual(remove_expired_bookings(self.db_path, self.uploads, date(2027, 2, 1)), 1)
        self.assertFalse((Path(self.uploads) / stored_name).exists())
        with connect_db(self.db_path) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM bookings").fetchone()[0], 0)


class DateTests(unittest.TestCase):
    def test_monday_cutoff_excludes_next_day(self):
        before = MONDAY.replace(hour=19, minute=59)
        after = MONDAY.replace(hour=20, minute=0)
        self.assertEqual(upcoming_tuesdays(before)[0].isoformat(), "2026-10-20")
        self.assertEqual(upcoming_tuesdays(after)[0].isoformat(), "2026-10-27")

    def test_last_slot_ends_at_1145(self):
        self.assertEqual(slot_end("11:30"), "11:45")


if __name__ == "__main__":
    unittest.main()
