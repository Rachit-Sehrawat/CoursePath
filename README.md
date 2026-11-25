# CoursePath

CoursePath is a Python command-line prototype for college course planning and academic progress. This starter implements **Member 1: Course & Student Management** and **Member 2: Prerequisite & Eligibility System**. The five-member project also includes Semester & Credit Planner, Timetable & Conflict Manager, and Academic Progress & Reports; those modules remain pending and are not represented as implemented here.

## Requirements and setup

- Python 3.10 or newer (uses only the Python standard library).
- Open a terminal in this folder, then run `python main.py` (or `py main.py` on Windows).
- The program loads sample CSVs from `data/` and writes changes there. Back up the data before experimenting with real records. Sample people are fictitious.

## Implemented functions

- Add, list, search, update and delete course records.
- Add, list, search, update and delete student records.
- Store course codes, names, credits, semester numbers and prerequisite codes.
- Store program, batch/section and completed course codes for each student.
- Check an individual student's eligibility, show missing prerequisites, or list eligible courses.
- Validate IDs, required fields, numeric bounds, duplicates and course-code references. Prevent deletion of a course referenced elsewhere.
- Persist through one shared CSV interface.

## Files

| File | Purpose |
| --- | --- |
| `main.py` | Runnable menu and input/output |
| `course_management.py` | Member 1 operations and integration getters |
| `eligibility.py` | Member 2 eligibility logic |
| `csv_store.py` | Shared schemas, CSV read/write and code-list helpers |
| `data/courses.csv` | Sample course records |
| `data/students.csv` | Sample student records |
| `tests/test_coursepath.py` | Repeatable standard-library tests |

## CSV schemas

`courses.csv`: `course_code,course_name,credits,semester,prerequisites`.
`students.csv`: `student_id,name,program,batch_section,completed_courses`.

List fields use `|` inside CSV cells (for example `CS101|CS102`). In the menu, enter multiple codes separated by commas. Use stable course codes across modules. Coordinate any column changes with the team.

## Interfaces for Members 3 to 5

Import shared data and public functions instead of keeping duplicate records:

```python
from csv_store import CSVStore
from course_management import list_courses, get_course, get_student
from eligibility import check_eligibility

store = CSVStore()
courses = list_courses(store)  # list of dictionaries
course = get_course(store, "CS102")  # dictionary or None
student = get_student(store, "STU1001")  # dictionary or None
decision = check_eligibility(store, "STU1001", "CS102")
```

The eligibility result includes `eligible`, `prerequisites`, `completed_prerequisites`, and `missing_prerequisites`. Member 3 can use course `credits` and `semester`; Member 4 can add a coordinated timetable schema; Member 5 can total credits from `completed_courses`. Agree on new schemas before implementation. All modules should use the same `CSVStore` and data directory.

## Run the tests

From this folder run `python -m unittest discover -s tests -v`. The tests cover persistence, record operations, validation, multiple prerequisites, eligibility results and safe deletion.

## Scope, limitations and status

This is a local, single-user educational prototype. It does not authenticate users, enforce privacy or concurrent access, connect to a college database, schedule semesters, calculate degree requirements, or manage timetable conflicts. Eligibility checks exact course codes and require every listed prerequisite; equivalencies, co-requisites and GPA rules are not modeled. CSV files are not encrypted.

**Completion status:** Member 1 = implemented; Member 2 = implemented; Members 3–5 = pending. If the five modules are weighted equally, the project is **40% complete by module count** (two of five modules). This is not a measure of overall project completion and should be reconciled with the instructor's rubric. Verify student, enrollment, team, instructor and submission details in the report before submitting; no unverified teammate contribution is claimed here.

## GitHub public repository setup

Nothing has been published. To publish it yourself:

1. Sign in to GitHub and choose **New repository**. Name it `CoursePath`; choose **Public** only if your team and instructor agree.
2. Do not initialize it with a README, since this folder already contains one.
3. Install Git if needed. In a terminal opened in this folder, replace `YOUR-USERNAME` and run:

```text
git init
git add .
git commit -m "Add CoursePath member 1 and 2 starter"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/CoursePath.git
git push -u origin main
```

4. Sign in through Git Credential Manager when prompted. Never put a password or token in the remote URL or commit secrets.
5. Confirm the files appear online. For team work, add collaborators or use pull requests, agree on shared CSV schemas, and review changes before merging. Public repositories can be seen by anyone; remove real student records and private information before publishing.
