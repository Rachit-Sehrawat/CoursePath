"""CoursePath text menu for completed Member 1 and Member 2 modules."""
from csv_store import CSVStore, split_codes
import course_management as cm
from eligibility import check_eligibility, eligible_courses


def ask(prompt):
    return input(prompt).strip()


def ask_codes(prompt):
    return [x.strip().upper() for x in ask(prompt).split(",") if x.strip()]


def show_courses(store):
    rows = cm.list_courses(store)
    if not rows:
        print("No courses found.")
    for r in rows:
        print(f"{r['course_code']} | {r['course_name']} | {r['credits']} credits | semester {r['semester']} | prerequisites: {', '.join(split_codes(r['prerequisites'])) or 'None'}")


def show_students(store):
    rows = cm.list_students(store)
    if not rows:
        print("No students found.")
    for r in rows:
        print(f"{r['student_id']} | {r['name']} | {r['program']} | {r['batch_section']} | completed: {', '.join(split_codes(r['completed_courses'])) or 'None'}")


def course_menu(store):
    while True:
        print("\nCOURSE MANAGEMENT\n1 Add  2 View/Search  3 Update  4 Delete  0 Back")
        choice = ask("> ")
        try:
            if choice == "1":
                cm.add_course(store, ask("Course code: "), ask("Course name: "), ask("Credits: "), ask("Semester: "), ask_codes("Prerequisite codes (comma separated, blank if none): "))
                print("Course added.")
            elif choice == "2":
                query = ask("Search code/name (blank lists all): ")
                for r in cm.search_courses(store, query):
                    print(f"{r['course_code']} | {r['course_name']} | {r['credits']} credits | semester {r['semester']} | prerequisites: {', '.join(split_codes(r['prerequisites'])) or 'None'}")
            elif choice == "3":
                code = ask("Course code: ")
                print("Leave a field blank to keep current value.")
                changes = {}
                for field, prompt in (("course_name", "New name"), ("credits", "New credits"), ("semester", "New semester")):
                    value = ask(prompt + ": ")
                    if value: changes[field] = value
                prereq = ask("New prerequisite codes (comma separated; type - to clear; blank to keep): ")
                if prereq: changes["prerequisites"] = [] if prereq == "-" else [x.strip() for x in prereq.split(",") if x.strip()]
                cm.update_course(store, code, **changes); print("Course updated.")
            elif choice == "4":
                cm.delete_course(store, ask("Course code: ")); print("Course deleted.")
            elif choice == "0": return
            else: print("Choose 0-4.")
        except (ValueError, OSError) as exc: print(f"Error: {exc}")


def student_menu(store):
    while True:
        print("\nSTUDENT MANAGEMENT\n1 Add  2 View/Search  3 Update  4 Delete  0 Back")
        choice = ask("> ")
        try:
            if choice == "1":
                cm.add_student(store, ask("Student ID: "), ask("Name: "), ask("Program: "), ask("Batch/section: "), ask_codes("Completed course codes (comma separated): ")); print("Student added.")
            elif choice == "2":
                query = ask("Search ID/name/program (blank lists all): ")
                for r in cm.search_students(store, query):
                    print(f"{r['student_id']} | {r['name']} | {r['program']} | {r['batch_section']} | completed: {', '.join(split_codes(r['completed_courses'])) or 'None'}")
            elif choice == "3":
                sid = ask("Student ID: "); print("Leave a field blank to keep current value."); changes = {}
                for field, prompt in (("name", "New name"), ("program", "New program"), ("batch_section", "New batch/section")):
                    value = ask(prompt + ": ")
                    if value: changes[field] = value
                codes = ask("New completed course codes (comma separated; type - to clear; blank to keep): ")
                if codes: changes["completed_courses"] = [] if codes == "-" else [x.strip() for x in codes.split(",") if x.strip()]
                cm.update_student(store, sid, **changes); print("Student updated.")
            elif choice == "4": cm.delete_student(store, ask("Student ID: ")); print("Student deleted.")
            elif choice == "0": return
            else: print("Choose 0-4.")
        except (ValueError, OSError) as exc: print(f"Error: {exc}")


def eligibility_menu(store):
    while True:
        print("\nPREREQUISITE & ELIGIBILITY\n1 Check a course  2 List eligible courses  0 Back")
        choice = ask("> ")
        try:
            if choice == "1":
                result = check_eligibility(store, ask("Student ID: "), ask("Course code: "))
                print(f"{result['student_name']} - {result['course_code']} {result['course_name']}")
                print("Prerequisites:", ", ".join(result["prerequisites"]) or "None")
                print("Missing:", ", ".join(result["missing_prerequisites"]) or "None")
                print("Result:", "ELIGIBLE" if result["eligible"] else "NOT ELIGIBLE")
            elif choice == "2":
                sid = ask("Student ID: ")
                for r in eligible_courses(store, sid): print(f"{r['course_code']} | {'Eligible' if r['eligible'] else 'Missing: ' + ', '.join(r['missing_prerequisites'])}")
            elif choice == "0": return
            else: print("Choose 0-2.")
        except (ValueError, OSError) as exc: print(f"Error: {exc}")


def main():
    store = CSVStore(); store.ensure_files()
    while True:
        print("\n===== COURSEPATH =====\n1 Course management\n2 Student management\n3 Prerequisite & eligibility\n4 View all courses\n5 View all students\n0 Exit")
        choice = ask("> ")
        if choice == "1": course_menu(store)
        elif choice == "2": student_menu(store)
        elif choice == "3": eligibility_menu(store)
        elif choice == "4": show_courses(store)
        elif choice == "5": show_students(store)
        elif choice == "0": print("Goodbye."); break
        else: print("Choose 0-5.")


if __name__ == "__main__":
    main()
