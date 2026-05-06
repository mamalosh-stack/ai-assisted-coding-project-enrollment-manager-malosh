# Enrollment Backend Structure Analysis

## Purpose

This analysis reviews the current student enrollment backend starter code before refactoring. The goal is to identify structural issues, layer-design problems, and maintainability risks without rewriting the project yet.

The current code works, but it is procedural and mixes several backend responsibilities in one file. The main responsibilities include SQLite setup, SQL queries, enrollment key rules, student enrollment actions, summary counts, sample data, and JSON snapshot export.

## Structural Issues Table

| Area / Function | Current Design Issue | Layer Problem | Why This Can Hurt Maintainability or Scalability | Future Design Direction |
|---|---|---|---|---|
| `DB_PATH`, `SNAPSHOT_PATH`, statuses, `CURRENT_STUDENT` | Configuration values and sample user data are stored as global variables. | Config and app state are mixed into the main backend file. | As the app grows, it becomes harder to change paths, statuses, or current student data without editing the main logic file. It also makes the code less flexible for multiple users or environments. | Move stable values into a constants/config area. Avoid treating sample student data as permanent app state. |
| `AVAILABLE_COURSE_KEYS` and `SAMPLE_ENROLLMENTS` | Seed data is hardcoded directly in the backend file. | Sample data and database setup are closely tied together. | This is fine for practice, but it would not scale well if courses, keys, or enrollments needed to come from real input or another source. | Keep as sample data for now, but separate from service logic. It could live near database setup or config. |
| `connect` | Every database operation depends on the same global `DB_PATH`. | Database connection logic is separate, but still globally configured. | If the project needs a different database path for testing or deployment, the global path makes that harder to change. | Put connection behavior in a database class so the path can be passed in or managed in one place. |
| `create_tables` | Table creation is handled as a standalone procedure. | Database schema setup is mixed into the same file as student actions. | This is manageable now, but future schema changes could clutter the main backend file. | Move schema setup into an `EnrollmentDatabase` class or database setup section. |
| `seed_sample_data` | The function inserts both course records and enrollment records using global seed lists. | Database work is mixed with sample-data setup. | This function has more than one setup job. If course seeding and enrollment seeding change separately, this function becomes harder to maintain. | Keep seeding in the database layer, but consider separating course seed and enrollment seed responsibilities later. |
| `rows_to_dicts` | Converts SQLite rows into dictionaries. | This is database-adjacent formatting. | It is useful, but if it spreads across the project, row conversion could become inconsistent. | Keep it close to the database layer as a helper. |
| `get_available_course_keys` | Runs a SQL query and returns course key records. | Database responsibility. | This is mostly clean, but it exposes enrollment keys directly. If display rules change later, a service layer may need to decide what should be shown. | Keep SQL in the database class. Let service logic decide how the data is used. |
| `get_course_by_key` | Looks up a course by enrollment key and normalizes the key using `strip().upper()`. | Mostly database, but includes a small service-level cleanup rule. | Input normalization is a rule about how enrollment keys should be handled. If similar cleanup is needed elsewhere, it could be repeated or hidden inside database code. | Consider moving key validation/normalization to the service layer while keeping the SQL lookup in the database layer. |
| `get_student_enrollments` | Queries active enrollments for a user. | Database query with a status rule. | The query is database work, but the meaning of “currently enrolled” depends on the service rule that status must equal `enrolled`. If business rules change, SQL queries may need to be updated in several places. | Keep the query in the database layer, but let the service layer define what the dashboard considers active enrollment. |
| `get_student_enrollment_history` | Returns all enrollment records for a student. | Database responsibility. | This is mostly clean, but it is still tied to the exact table structure and joined output. | Move to database class as a repository-style method. |
| `enroll_with_key` | Validates input, checks email format, looks up a course, inserts or updates an enrollment, and returns a record. | Mixed service and database responsibility. | This is one of the biggest structural issues. The function handles business rules and directly performs database writes. As enrollment rules grow, this function could become large and difficult to test. | Split into service and database layers. The service should validate enrollment rules, while the database class should handle lookup and insert/update operations. |
| `soft_unenroll_student` | Represents a student action but directly performs a SQL `UPDATE`. | Mixed service and database responsibility. | The function decides the meaning of unenrolling while also changing database rows. If unenrollment rules become more complex, this function may become harder to maintain. | Service should decide whether a student can unenroll. Database layer should perform the status update. |
| `get_student_summary` | Builds summary counts by calling enrollment history and interpreting statuses. | Service responsibility that depends on database output. | This function creates dashboard-style meaning from records. If summary rules change, the service layer should control that logic instead of mixing it with database access. | Move to service class. It can call database methods but should own the summary counting logic. |
| `get_all_enrollment_records` | Runs a SQL query to return all enrollment records for the snapshot. | Database responsibility. | This is mostly clean database work, but it exists mainly because the snapshot export needs it. | Keep in database class. Snapshot/export logic can call it. |
| `export_database_snapshot` | Collects current student, available course keys, enrollment records, and writes JSON. | Mixed config, database, and export responsibility. | This function does several jobs at once. It reads global state, calls database functions, shapes snapshot data, and writes to a file. This can become harder to change if the export format or data source changes. | Split export behavior from database/service logic. Keep JSON writing separate from enrollment rules. |
| SQLite `SELECT`, `INSERT`, `UPDATE` statements | SQL is spread across several standalone functions. | Database logic is distributed across the file. | As the project grows, scattered SQL makes it harder to update schema, reuse queries, or test database behavior. | Centralize SQL work in an `EnrollmentDatabase` class. |
| `main` runner / top-level test flow | The main function creates tables, seeds data, prints outputs, tests enrollment, gets summaries, and exports a snapshot. | Mixed orchestration, testing, service calls, and database setup. | The runner is useful for practice, but it should not become the main place where app logic lives. If more behavior is added here, it becomes hard to separate testing from real backend behavior. | Keep `main` as a small test runner that calls organized classes or methods. |

## Most Important Findings

1. The current code works, but it is procedural and has many responsibilities in one file.

2. Database responsibilities are spread across many functions instead of being grouped into one clear database layer.

3. Some database functions also make service-level decisions. For example, `get_course_by_key` normalizes the enrollment key, `get_student_enrollments` defines active enrollment using status, and `soft_unenroll_student` performs a student action while directly updating SQL.

4. `enroll_with_key` is the biggest mixed function because it validates user input, applies enrollment-key rules, finds the course, writes to the database, and returns the updated record.

5. `export_database_snapshot` is also mixed because it reads global state, gathers data from database functions, formats a snapshot dictionary, and writes JSON.

6. Global constants and sample data are acceptable for a starter file, but they should be separated from core backend logic as the app grows.

7. A clearer future design would separate the backend into:
   - a config/constants area for paths, statuses, and sample data
   - an `EnrollmentDatabase` class for SQLite connections, table setup, SQL queries, inserts, and updates
   - an `EnrollmentService` class for student actions, validation, enrollment-key rules, soft unenroll decisions, and summary logic
   - a small runner that only tests the flow without containing core logic

## Reflection

My method map helped show that the project is not broken, but it is structurally mixed. The main risk is that future features would require editing the same procedural file in many places. Separating database work from service rules would make the backend easier to test, update, and connect to the Streamlit UI in Session 2.