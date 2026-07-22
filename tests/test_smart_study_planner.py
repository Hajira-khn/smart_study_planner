"""
test_smart_study_planner.py
===========================
AI-generated test suite for the Smart Study Planner (CSE325 – Assignment 4).

Generated with assistance from Claude (Anthropic) based on the application's
requirements and user stories. Tests cover:
  - Authentication / login validation
  - Subject management (add, delete, search, progress update)
  - Study plan management (add, delete, filter)
  - Progress & statistics calculation
  - Edge cases and error handling

Run with:
    python -m pytest tests/ -v
or:
    python -m unittest discover -s tests -v
"""

import sys
import os
import unittest
from copy import deepcopy
from datetime import date

# Ensure project root is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logic import (
    validate_login,
    add_subject, delete_subject, search_subjects, update_progress,
    add_plan, delete_plan, filter_plans_by_priority,
    calculate_overall_progress, total_weekly_hours,
    DEFAULT_SUBJECTS, SUBJECTS_LIST, VALID_PRIORITIES, VALID_DURATIONS,
)

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def fresh_subjects():
    """Return a deep copy of default subjects so tests don't pollute each other."""
    return deepcopy(DEFAULT_SUBJECTS)


def fresh_plans():
    today = str(date.today())
    return [
        (today, "Programming",   "2 hours", "High",   "OOP patterns"),
        (today, "Mathematics",   "1 hour",  "Medium", "Integrals"),
        (today, "English",       "30 min",  "Low",    "Essay"),
    ]


# ═════════════════════════════════════════════════════════════
# 1.  AUTHENTICATION TESTS
# ═════════════════════════════════════════════════════════════
class TestLoginValidation(unittest.TestCase):

    # ── Functional (happy-path) ──────────────────────────────
    def test_valid_credentials_accepted(self):
        """Normal username and password should succeed."""
        ok, msg = validate_login("alice", "secret123")
        self.assertTrue(ok)
        self.assertEqual(msg, "Login successful.")

    def test_valid_credentials_with_spaces_trimmed(self):
        """Leading/trailing whitespace should be stripped before validation."""
        ok, msg = validate_login("  bob  ", "  pass  ")
        self.assertTrue(ok)

    def test_numeric_username_accepted(self):
        ok, _ = validate_login("12345678", "mypass")
        self.assertTrue(ok)

    # ── Error handling ───────────────────────────────────────
    def test_empty_username_rejected(self):
        ok, msg = validate_login("", "password")
        self.assertFalse(ok)
        self.assertIn("Username", msg)

    def test_empty_password_rejected(self):
        ok, msg = validate_login("alice", "")
        self.assertFalse(ok)
        self.assertIn("Password", msg)

    def test_both_empty_rejected(self):
        ok, msg = validate_login("", "")
        self.assertFalse(ok)

    # ── Edge cases ───────────────────────────────────────────
    def test_whitespace_only_username_rejected(self):
        """A username of only spaces is effectively empty."""
        ok, _ = validate_login("   ", "password")
        self.assertFalse(ok)

    def test_whitespace_only_password_rejected(self):
        ok, _ = validate_login("alice", "   ")
        self.assertFalse(ok)

    def test_very_long_username_accepted(self):
        """No hard length limit in the spec — should not crash."""
        ok, _ = validate_login("a" * 500, "pass")
        self.assertTrue(ok)

    def test_special_characters_in_credentials(self):
        ok, _ = validate_login("user@uni.edu", "P@$$w0rd!")
        self.assertTrue(ok)


# ═════════════════════════════════════════════════════════════
# 2.  SUBJECT MANAGEMENT TESTS
# ═════════════════════════════════════════════════════════════
class TestAddSubject(unittest.TestCase):

    def setUp(self):
        self.subjects = fresh_subjects()

    def test_add_valid_new_subject(self):
        ok, msg = add_subject(self.subjects, "Physics", hours=5)
        self.assertTrue(ok)
        self.assertEqual(self.subjects[-1]["name"], "Physics")

    def test_new_subject_has_zero_progress(self):
        add_subject(self.subjects, "Chemistry", hours=3)
        new = next(s for s in self.subjects if s["name"] == "Chemistry")
        self.assertEqual(new["progress"], 0)

    def test_duplicate_subject_rejected(self):
        ok, msg = add_subject(self.subjects, "Programming")  # already in default
        self.assertFalse(ok)
        self.assertIn("already exists", msg)

    def test_duplicate_case_insensitive(self):
        ok, _ = add_subject(self.subjects, "PROGRAMMING")
        self.assertFalse(ok)

    def test_empty_name_rejected(self):
        ok, msg = add_subject(self.subjects, "")
        self.assertFalse(ok)

    def test_whitespace_only_name_rejected(self):
        ok, _ = add_subject(self.subjects, "   ")
        self.assertFalse(ok)

    def test_hours_too_low_rejected(self):
        ok, msg = add_subject(self.subjects, "Art", hours=0)
        self.assertFalse(ok)
        self.assertIn("hours", msg.lower())

    def test_hours_too_high_rejected(self):
        ok, _ = add_subject(self.subjects, "Art", hours=41)
        self.assertFalse(ok)

    def test_boundary_hours_1_accepted(self):
        ok, _ = add_subject(self.subjects, "Art", hours=1)
        self.assertTrue(ok)

    def test_boundary_hours_40_accepted(self):
        ok, _ = add_subject(self.subjects, "Drama", hours=40)
        self.assertTrue(ok)

    def test_subject_count_increments(self):
        before = len(self.subjects)
        add_subject(self.subjects, "Biology", hours=4)
        self.assertEqual(len(self.subjects), before + 1)


class TestDeleteSubject(unittest.TestCase):

    def setUp(self):
        self.subjects = fresh_subjects()

    def test_delete_existing_subject(self):
        ok, _ = delete_subject(self.subjects, "English")
        self.assertTrue(ok)
        names = [s["name"] for s in self.subjects]
        self.assertNotIn("English", names)

    def test_delete_nonexistent_subject(self):
        ok, msg = delete_subject(self.subjects, "Biology")
        self.assertFalse(ok)
        self.assertIn("not found", msg)

    def test_delete_reduces_count(self):
        before = len(self.subjects)
        delete_subject(self.subjects, "Mathematics")
        self.assertEqual(len(self.subjects), before - 1)

    def test_delete_from_empty_list(self):
        ok, _ = delete_subject([], "Anything")
        self.assertFalse(ok)


class TestSearchSubjects(unittest.TestCase):

    def setUp(self):
        self.subjects = fresh_subjects()

    def test_search_returns_matching_subjects(self):
        result = search_subjects(self.subjects, "math")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Mathematics")

    def test_search_case_insensitive(self):
        result = search_subjects(self.subjects, "ENGLISH")
        self.assertEqual(len(result), 1)

    def test_empty_query_returns_all(self):
        result = search_subjects(self.subjects, "")
        self.assertEqual(len(result), len(self.subjects))

    def test_no_match_returns_empty_list(self):
        result = search_subjects(self.subjects, "zzznomatch")
        self.assertEqual(result, [])

    def test_partial_match_works(self):
        result = search_subjects(self.subjects, "intel")  # "Artificial Intelligence"
        self.assertEqual(len(result), 1)


class TestUpdateProgress(unittest.TestCase):

    def setUp(self):
        self.subjects = fresh_subjects()

    def test_update_valid_progress(self):
        ok, _ = update_progress(self.subjects, "English", 95)
        self.assertTrue(ok)
        eng = next(s for s in self.subjects if s["name"] == "English")
        self.assertEqual(eng["progress"], 95)

    def test_progress_boundary_zero(self):
        ok, _ = update_progress(self.subjects, "English", 0)
        self.assertTrue(ok)

    def test_progress_boundary_100(self):
        ok, _ = update_progress(self.subjects, "English", 100)
        self.assertTrue(ok)

    def test_progress_above_100_rejected(self):
        ok, _ = update_progress(self.subjects, "English", 101)
        self.assertFalse(ok)

    def test_progress_negative_rejected(self):
        ok, _ = update_progress(self.subjects, "English", -1)
        self.assertFalse(ok)

    def test_nonexistent_subject_returns_error(self):
        ok, msg = update_progress(self.subjects, "Biology", 50)
        self.assertFalse(ok)
        self.assertIn("not found", msg)


# ═════════════════════════════════════════════════════════════
# 3.  STUDY PLAN TESTS
# ═════════════════════════════════════════════════════════════
class TestAddPlan(unittest.TestCase):

    def setUp(self):
        self.plans = []
        self.today = str(date.today())

    def test_add_valid_plan(self):
        ok, _ = add_plan(self.plans, self.today,
                         "Programming", "2 hours", "High", "Review notes")
        self.assertTrue(ok)
        self.assertEqual(len(self.plans), 1)

    def test_plan_stored_correctly(self):
        add_plan(self.plans, self.today, "English", "1 hour", "Low", "Grammar")
        self.assertEqual(self.plans[0][1], "English")
        self.assertEqual(self.plans[0][3], "Low")

    def test_empty_date_rejected(self):
        ok, _ = add_plan(self.plans, "", "Programming", "1 hour", "High")
        self.assertFalse(ok)

    def test_invalid_date_format_rejected(self):
        ok, _ = add_plan(self.plans, "16/07/2026", "Programming", "1 hour", "High")
        self.assertFalse(ok)

    def test_impossible_date_rejected(self):
        ok, _ = add_plan(self.plans, "2026-13-45", "Programming", "1 hour", "High")
        self.assertFalse(ok)

    def test_invalid_subject_rejected(self):
        ok, msg = add_plan(self.plans, self.today,
                           "Underwater Basket Weaving", "1 hour", "High")
        self.assertFalse(ok)
        self.assertIn("Invalid subject", msg)

    def test_invalid_duration_rejected(self):
        ok, _ = add_plan(self.plans, self.today,
                         "Programming", "45 minutes", "High")
        self.assertFalse(ok)

    def test_invalid_priority_rejected(self):
        ok, _ = add_plan(self.plans, self.today,
                         "Programming", "1 hour", "Urgent")
        self.assertFalse(ok)

    def test_empty_notes_stored_as_dash(self):
        add_plan(self.plans, self.today, "Mathematics", "30 min", "Low")
        self.assertEqual(self.plans[0][4], "—")

    def test_all_valid_durations_accepted(self):
        for dur in VALID_DURATIONS:
            ok, _ = add_plan(self.plans, self.today,
                             "Programming", dur, "Medium")
            self.assertTrue(ok, f"Duration '{dur}' should be valid")

    def test_all_valid_priorities_accepted(self):
        for pri in VALID_PRIORITIES:
            ok, _ = add_plan(self.plans, self.today,
                             "English", "1 hour", pri)
            self.assertTrue(ok, f"Priority '{pri}' should be valid")


class TestDeletePlan(unittest.TestCase):

    def setUp(self):
        self.plans = fresh_plans()

    def test_delete_valid_index(self):
        before = len(self.plans)
        ok, _ = delete_plan(self.plans, 0)
        self.assertTrue(ok)
        self.assertEqual(len(self.plans), before - 1)

    def test_delete_last_index(self):
        ok, _ = delete_plan(self.plans, len(self.plans) - 1)
        self.assertTrue(ok)

    def test_delete_negative_index_rejected(self):
        ok, _ = delete_plan(self.plans, -1)
        self.assertFalse(ok)

    def test_delete_out_of_range_rejected(self):
        ok, _ = delete_plan(self.plans, 999)
        self.assertFalse(ok)

    def test_delete_from_empty_list(self):
        ok, _ = delete_plan([], 0)
        self.assertFalse(ok)


class TestFilterPlansByPriority(unittest.TestCase):

    def setUp(self):
        self.plans = fresh_plans()
        # plans: High, Medium, Low

    def test_filter_high_priority(self):
        result = filter_plans_by_priority(self.plans, "High")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Programming")

    def test_filter_medium_priority(self):
        result = filter_plans_by_priority(self.plans, "Medium")
        self.assertEqual(len(result), 1)

    def test_filter_low_priority(self):
        result = filter_plans_by_priority(self.plans, "Low")
        self.assertEqual(len(result), 1)

    def test_invalid_priority_returns_empty(self):
        result = filter_plans_by_priority(self.plans, "Critical")
        self.assertEqual(result, [])

    def test_no_matching_plans_returns_empty(self):
        plans_all_high = [(p[0], p[1], p[2], "High", p[4]) for p in self.plans]
        result = filter_plans_by_priority(plans_all_high, "Low")
        self.assertEqual(result, [])


# ═════════════════════════════════════════════════════════════
# 4.  PROGRESS & STATISTICS TESTS
# ═════════════════════════════════════════════════════════════
class TestProgressStatistics(unittest.TestCase):

    def setUp(self):
        self.subjects = fresh_subjects()
        # Default progress values: 78, 62, 45, 90, 55 → avg = 66.0

    def test_overall_progress_correct(self):
        result = calculate_overall_progress(self.subjects)
        expected = round((78 + 62 + 45 + 90 + 55) / 5, 2)
        self.assertAlmostEqual(result, expected, places=2)

    def test_overall_progress_empty_list(self):
        result = calculate_overall_progress([])
        self.assertEqual(result, 0.0)

    def test_overall_progress_all_zero(self):
        subjects = [{"name": "X", "hours": 2, "progress": 0},
                    {"name": "Y", "hours": 3, "progress": 0}]
        self.assertEqual(calculate_overall_progress(subjects), 0.0)

    def test_overall_progress_all_100(self):
        subjects = [{"name": "X", "hours": 2, "progress": 100},
                    {"name": "Y", "hours": 3, "progress": 100}]
        self.assertEqual(calculate_overall_progress(subjects), 100.0)

    def test_total_weekly_hours_correct(self):
        result = total_weekly_hours(self.subjects)
        expected = 10 + 8 + 6 + 4 + 9   # = 37
        self.assertEqual(result, expected)

    def test_total_weekly_hours_empty(self):
        self.assertEqual(total_weekly_hours([]), 0)

    def test_total_weekly_hours_single_subject(self):
        self.assertEqual(total_weekly_hours([{"name": "X", "hours": 7, "progress": 0}]), 7)


# ═════════════════════════════════════════════════════════════
# 5.  INTEGRATION-STYLE TESTS  (multi-step workflows)
# ═════════════════════════════════════════════════════════════
class TestWorkflows(unittest.TestCase):

    def test_full_add_then_delete_subject(self):
        subjects = fresh_subjects()
        add_subject(subjects, "Chemistry", hours=5)
        self.assertTrue(any(s["name"] == "Chemistry" for s in subjects))
        delete_subject(subjects, "Chemistry")
        self.assertFalse(any(s["name"] == "Chemistry" for s in subjects))

    def test_progress_affects_overall_calculation(self):
        subjects = [{"name": "X", "hours": 5, "progress": 50}]
        update_progress(subjects, "X", 80)
        self.assertEqual(calculate_overall_progress(subjects), 80.0)

    def test_add_plan_then_filter(self):
        plans = []
        today = str(date.today())
        add_plan(plans, today, "Programming", "2 hours", "High", "Test")
        add_plan(plans, today, "English",     "1 hour",  "Low",  "Essay")
        high_plans = filter_plans_by_priority(plans, "High")
        self.assertEqual(len(high_plans), 1)

    def test_login_then_add_subjects(self):
        """Simulate a user logging in and immediately adding subjects."""
        ok, _ = validate_login("student1", "pass123")
        self.assertTrue(ok)
        subjects = fresh_subjects()
        ok2, _ = add_subject(subjects, "Physics", hours=6)
        self.assertTrue(ok2)

    def test_search_after_delete(self):
        subjects = fresh_subjects()
        delete_subject(subjects, "Mathematics")
        result = search_subjects(subjects, "math")
        self.assertEqual(result, [])


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    unittest.main(verbosity=2)
