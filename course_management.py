"""Member 1: Course & Student Management operations and integration API."""
from __future__ import annotations

import re
from csv_store import CSVStore, split_codes, join_codes

COURSES = "courses.csv"
STUDENTS = "students.csv"


def _clean(value: str, field: str) -> str:
    value = str(value).strip()
    if not value:
        raise ValueError(f"{field} is required.")
    return value


def _course_map(store: CSVStore) -> dict[str, dict[str, str]]:
    return {r["course_code"].upper(): r for r in store.read(COURSES)}


def _student_map(store: CSVStore) -> dict[str, dict[str, str]]:
    return {r["student_id"].upper(): r for r in store.read(STUDENTS)}


def add_course(store: CSVStore, course_code: str, course_name: str, credits: int, semester: int, prerequisites=()) -> dict:
    code = _clean(course_code, "Course code").upper()
    if not re.fullmatch(r"[A-Z0-9_-]{2,16}", code):
        raise ValueError("Course code must be 2-16 letters, digits, underscores or hyphens.")
    if code in _course_map(store):
        raise ValueError(f"Course {code} already exists.")
    try:
        credits, semester = int(credits), int(semester)
    except (ValueError, TypeError):
        raise ValueError("Credits and semester must be whole numbers.") from None
    if not 1 <= credits <= 30 or not 1 <= semester <= 20:
        raise ValueError("Credits must be 1-30 and semester must be 1-20.")
    prereqs = [str(x).strip().upper() for x in prerequisites if str(x).strip()]
    existing = _course_map(store)
    if code in prereqs or len(set(prereqs)) != len(prereqs):
        raise ValueError("A course cannot require itself or list a prerequisite twice.")
    missing = [p for p in prereqs if p not in existing]
    if missing:
        raise ValueError(f"Unknown prerequisite course code(s): {', '.join(missing)}.")
    row = {"course_code": code, "course_name": _clean(course_name, "Course name"), "credits": str(credits),
           "semester": str(semester), "prerequisites": join_codes(prereqs)}
    rows = store.read(COURSES) + [row]
    store.write(COURSES, rows)
    return row


def update_course(store: CSVStore, course_code: str, **changes) -> dict:
    code = _clean(course_code, "Course code").upper()
    rows = store.read(COURSES)
    target = next((r for r in rows if r["course_code"].upper() == code), None)
    if not target:
        raise ValueError(f"Course {code} was not found.")
    updated = dict(target)
    if "course_name" in changes:
        updated["course_name"] = _clean(changes["course_name"], "Course name")
    for field, low, high in (("credits", 1, 30), ("semester", 1, 20)):
        if field in changes:
            try:
                number = int(changes[field])
            except (ValueError, TypeError):
                raise ValueError(f"{field.title()} must be a whole number.") from None
            if not low <= number <= high:
                raise ValueError(f"{field.title()} must be {low}-{high}.")
            updated[field] = str(number)
    if "prerequisites" in changes:
        prereqs = [str(x).strip().upper() for x in changes["prerequisites"] if str(x).strip()]
        course_map = _course_map(store)
        missing = [p for p in prereqs if p not in course_map]
        if code in prereqs or len(set(prereqs)) != len(prereqs) or missing:
            raise ValueError("Prerequisites must be existing course codes, without duplicates or self-reference.")
        def depends_on(candidate: str, sought: str, seen: set[str]) -> bool:
            if candidate == sought:
                return True
            if candidate in seen:
                return False
            seen.add(candidate)
            return any(depends_on(parent, sought, seen) for parent in split_codes(course_map[candidate]["prerequisites"]))
        if any(depends_on(parent, code, set()) for parent in prereqs):
            raise ValueError("Prerequisite changes cannot create a circular course dependency.")
        updated["prerequisites"] = join_codes(prereqs)
    store.write(COURSES, [updated if r["course_code"].upper() == code else r for r in rows])
    return updated


def delete_course(store: CSVStore, course_code: str) -> None:
    code = _clean(course_code, "Course code").upper()
    courses = store.read(COURSES)
    if not any(r["course_code"].upper() == code for r in courses):
        raise ValueError(f"Course {code} was not found.")
    dependents = [r["course_code"] for r in courses if code in split_codes(r["prerequisites"])]
    completed_by = [r["student_id"] for r in store.read(STUDENTS) if code in split_codes(r["completed_courses"])]
    if dependents or completed_by:
        raise ValueError("Cannot delete: course is referenced by prerequisites or student completion records.")
    store.write(COURSES, [r for r in courses if r["course_code"].upper() != code])


def search_courses(store: CSVStore, query: str = "") -> list[dict[str, str]]:
    q = query.strip().casefold()
    return [r for r in store.read(COURSES) if not q or q in r["course_code"].casefold() or q in r["course_name"].casefold()]


def add_student(store: CSVStore, student_id: str, name: str, program: str, batch_section: str, completed_courses=()) -> dict:
    sid = _clean(student_id, "Student ID").upper()
    if not re.fullmatch(r"[A-Z0-9_-]{3,24}", sid):
        raise ValueError("Student ID must be 3-24 letters, digits, underscores or hyphens.")
    if sid in _student_map(store):
        raise ValueError(f"Student {sid} already exists.")
    course_map = _course_map(store)
    completed = [str(x).strip().upper() for x in completed_courses if str(x).strip()]
    if len(set(completed)) != len(completed) or any(c not in course_map for c in completed):
        raise ValueError("Completed courses must be valid course codes with no duplicates.")
    row = {"student_id": sid, "name": _clean(name, "Student name"), "program": _clean(program, "Program"),
           "batch_section": _clean(batch_section, "Batch/section"), "completed_courses": join_codes(completed)}
    store.write(STUDENTS, store.read(STUDENTS) + [row])
    return row


def update_student(store: CSVStore, student_id: str, **changes) -> dict:
    sid = _clean(student_id, "Student ID").upper()
    rows = store.read(STUDENTS)
    target = next((r for r in rows if r["student_id"].upper() == sid), None)
    if not target:
        raise ValueError(f"Student {sid} was not found.")
    updated = dict(target)
    for field, label in (("name", "Student name"), ("program", "Program"), ("batch_section", "Batch/section")):
        if field in changes:
            updated[field] = _clean(changes[field], label)
    if "completed_courses" in changes:
        codes = [str(x).strip().upper() for x in changes["completed_courses"] if str(x).strip()]
        course_map = _course_map(store)
        if len(set(codes)) != len(codes) or any(c not in course_map for c in codes):
            raise ValueError("Completed courses must be valid course codes with no duplicates.")
        updated["completed_courses"] = join_codes(codes)
    store.write(STUDENTS, [updated if r["student_id"].upper() == sid else r for r in rows])
    return updated


def delete_student(store: CSVStore, student_id: str) -> None:
    sid = _clean(student_id, "Student ID").upper()
    rows = store.read(STUDENTS)
    if not any(r["student_id"].upper() == sid for r in rows):
        raise ValueError(f"Student {sid} was not found.")
    store.write(STUDENTS, [r for r in rows if r["student_id"].upper() != sid])


def search_students(store: CSVStore, query: str = "") -> list[dict[str, str]]:
    q = query.strip().casefold()
    return [r for r in store.read(STUDENTS) if not q or any(q in r[k].casefold() for k in ("student_id", "name", "program", "batch_section"))]


# Integration interfaces: return plain dictionaries/lists for Members 3-5.
def get_course(store: CSVStore, course_code: str) -> dict[str, str] | None:
    return _course_map(store).get(course_code.strip().upper())


def get_student(store: CSVStore, student_id: str) -> dict[str, str] | None:
    return _student_map(store).get(student_id.strip().upper())


def list_courses(store: CSVStore) -> list[dict[str, str]]:
    return store.read(COURSES)


def list_students(store: CSVStore) -> list[dict[str, str]]:
    return store.read(STUDENTS)
