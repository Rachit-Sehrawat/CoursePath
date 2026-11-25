"""Member 2: Prerequisite & Eligibility System."""
from csv_store import CSVStore, split_codes
from course_management import get_course, get_student


def get_prerequisites(store: CSVStore, course_code: str) -> list[str]:
    course = get_course(store, course_code)
    if course is None:
        raise ValueError(f"Course {course_code.strip().upper()} was not found.")
    return split_codes(course["prerequisites"])


def check_eligibility(store: CSVStore, student_id: str, course_code: str) -> dict:
    student = get_student(store, student_id)
    if student is None:
        raise ValueError(f"Student {student_id.strip().upper()} was not found.")
    course = get_course(store, course_code)
    if course is None:
        raise ValueError(f"Course {course_code.strip().upper()} was not found.")
    completed = set(split_codes(student["completed_courses"]))
    prerequisites = get_prerequisites(store, course["course_code"])
    missing = [code for code in prerequisites if code not in completed]
    return {"student_id": student["student_id"], "student_name": student["name"],
            "course_code": course["course_code"], "course_name": course["course_name"],
            "prerequisites": prerequisites, "completed_prerequisites": [c for c in prerequisites if c in completed],
            "missing_prerequisites": missing, "eligible": not missing}


def eligible_courses(store: CSVStore, student_id: str) -> list[dict]:
    student = get_student(store, student_id)
    if student is None:
        raise ValueError(f"Student {student_id.strip().upper()} was not found.")
    return [check_eligibility(store, student_id, c["course_code"]) for c in store.read("courses.csv")]
