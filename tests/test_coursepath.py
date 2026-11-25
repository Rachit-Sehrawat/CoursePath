import tempfile
import unittest
from pathlib import Path
from csv_store import CSVStore
import course_management as cm
from eligibility import check_eligibility, eligible_courses

class CoursePathTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = CSVStore(Path(self.temp.name)); self.store.ensure_files()
        cm.add_course(self.store, "CS101", "Programming Fundamentals", 4, 1)
        cm.add_course(self.store, "CS102", "Data Structures", 4, 2, ["CS101"])
        cm.add_course(self.store, "CS201", "Algorithms", 4, 3, ["CS102"])
        cm.add_student(self.store, "STU1001", "Aarav", "Computer Science", "B47", ["CS101"])
    def tearDown(self): self.temp.cleanup()
    def test_eligibility_and_missing_prerequisite(self):
        self.assertTrue(check_eligibility(self.store, "stu1001", "cs102")["eligible"])
        result = check_eligibility(self.store, "STU1001", "CS201")
        self.assertFalse(result["eligible"]); self.assertEqual(result["missing_prerequisites"], ["CS102"])
    def test_multiple_prerequisites(self):
        cm.add_course(self.store, "CS301", "Advanced Systems", 3, 4, ["CS101", "CS102"])
        cm.update_student(self.store, "STU1001", completed_courses=["CS101", "CS102"])
        self.assertTrue(check_eligibility(self.store, "STU1001", "CS301")["eligible"])
    def test_crud_search_and_persistence(self):
        cm.update_course(self.store, "CS102", credits=5)
        self.assertEqual(cm.search_courses(self.store, "structures")[0]["credits"], "5")
        cm.add_student(self.store, "STU2002", "Bea", "CS", "B48")
        cm.update_student(self.store, "STU2002", name="Beatrice")
        self.assertEqual(cm.search_students(self.store, "beatrice")[0]["student_id"], "STU2002")
        self.assertEqual(CSVStore(Path(self.temp.name)).read("courses.csv")[1]["credits"], "5")
        cm.delete_student(self.store, "STU2002")
    def test_validation_and_safe_delete(self):
        with self.assertRaises(ValueError): cm.add_course(self.store, "CS102", "Duplicate", 4, 2)
        with self.assertRaises(ValueError): cm.add_course(self.store, "CS999", "Bad", 0, 2)
        with self.assertRaises(ValueError): cm.add_course(self.store, "CS500", "Unknown", 3, 4, ["MISSING"])
        with self.assertRaises(ValueError): cm.delete_course(self.store, "CS101")
    def test_rejects_circular_prerequisites(self):
        with self.assertRaisesRegex(ValueError, "circular"):
            cm.update_course(self.store, "CS101", prerequisites=["CS201"])
    def test_unknown_records(self):
        with self.assertRaisesRegex(ValueError, "was not found"): check_eligibility(self.store, "UNKNOWN", "CS102")
        with self.assertRaisesRegex(ValueError, "was not found"): check_eligibility(self.store, "STU1001", "UNKNOWN")
    def test_eligible_course_list(self):
        results = {r["course_code"]: r["eligible"] for r in eligible_courses(self.store, "STU1001")}
        self.assertEqual(results, {"CS101": True, "CS102": True, "CS201": False})

if __name__ == "__main__": unittest.main()
