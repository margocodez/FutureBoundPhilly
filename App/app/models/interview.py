import json
from dataclasses import dataclass, field

from app.models.db import get_db
from app.models.student import Student

# The 13 inputs Model B uses. Atlas must collect every one before finishing.
MODEL_B_FIELDS = [
    "submitted_fafsa_prior_to_graduation",
    "self_reported_attendance",
    "very_certain_attend_planned_college",
    "planned_enrollment_intensity",
    "unsure_what_semester_start",
    "concurrent_cc_enrollment",
    "registered_cc_prior_to_graduation",
    "parent_education",
    "cumulative_gpa",
    "ela_sbac_sd_units",
    "math_sbac_sd_units",
    "passed_ap_ib_course",
    "passed_ap_ib_exam",
]
# Enrollment context for the student's checklist. Not model inputs, but still required.
PROFILE_FIELDS = [
    "college_name",
    "school_type",
    "starting_term",
    "living_on_campus",
    "accepted",
    "accepted_offer",
    "paid_deposit",
]

# Students report a performance level; the model expects SD units (0 = average).
# These are rough midpoints for each level -- staff can override with real scores.
TEST_LEVEL_TO_SD = {
    "below_basic": -1.0,
    "basic": -0.35,
    "proficient": 0.35,
    "advanced": 1.1,
    "unknown": 0.0,
}

# Allowed values for each answer Atlas records (ranges for numbers, sets for codes).
ALLOWED = {
    "submitted_fafsa_prior_to_graduation": {0, 1},
    "self_reported_attendance": {0, 1, 2},
    "very_certain_attend_planned_college": {0, 1},
    "planned_enrollment_intensity": {0, 1, 2},
    "unsure_what_semester_start": {0, 1},
    "concurrent_cc_enrollment": {0, 1},
    "registered_cc_prior_to_graduation": {0, 1},
    "parent_education": {0, 1, 2, 3, 4},
    "passed_ap_ib_course": {0, 1},
    "passed_ap_ib_exam": {0, 1},
    "accepted": {0, 1},
    "accepted_offer": {0, 1},
    "paid_deposit": {0, 1},
}
# Profile answers stored as text codes.
ALLOWED_TEXT = {
    "school_type": {"trade", "2_year", "4_year", "unsure"},
    "starting_term": {"fall", "spring", "unsure"},
    "living_on_campus": {"yes", "no", "unsure"},
}
GPA_RANGE = (0.0, 4.3)


@dataclass
class Interview:
    id: int
    user_id: int
    status: str
    messages: list = field(default_factory=list)
    answers: dict = field(default_factory=dict)
    test_score_source: str = "student_estimate"
    risk_score: int = None
    risk_category: str = None

    @property
    def is_complete(self):
        return self.status == "complete"

    @classmethod
    def _from_row(cls, row):
        if row is None:
            return None
        return cls(row["id"], row["user_id"], row["status"], json.loads(row["messages"]),
                   json.loads(row["answers"]), row["test_score_source"],
                   row["risk_score"], row["risk_category"])

    @classmethod
    def latest_for_user(cls, user_id):
        row = get_db().execute(
            "SELECT * FROM interviews WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,)
        ).fetchone()
        return cls._from_row(row)

    @classmethod
    def get_or_start(cls, user_id):
        interview = cls.latest_for_user(user_id)
        if interview is None:
            conn = get_db()
            conn.execute("INSERT INTO interviews (user_id) VALUES (?)", (user_id,))
            conn.commit()
            interview = cls.latest_for_user(user_id)
        return interview

    def record_answers(self, data):
        """Validate and merge answers from Atlas. Returns a list of error strings."""
        errors = []
        for name, value in data.items():
            if name in ("ela_test_level", "math_test_level"):
                if value not in TEST_LEVEL_TO_SD:
                    errors.append(f"{name} must be one of {sorted(TEST_LEVEL_TO_SD)}")
                    continue
                subject = name.split("_")[0]
                self.answers[name] = value
                self.answers[f"{subject}_sbac_sd_units"] = TEST_LEVEL_TO_SD[value]
            elif name == "cumulative_gpa":
                try:
                    gpa = float(value)
                except (TypeError, ValueError):
                    gpa = None
                if gpa is None or not GPA_RANGE[0] <= gpa <= GPA_RANGE[1]:
                    errors.append(f"cumulative_gpa must be a number from {GPA_RANGE[0]} to {GPA_RANGE[1]}")
                    continue
                self.answers[name] = gpa
            elif name in ALLOWED:
                if value not in ALLOWED[name]:
                    errors.append(f"{name} must be one of {sorted(ALLOWED[name])}")
                    continue
                self.answers[name] = int(value)
            elif name in ALLOWED_TEXT:
                if value not in ALLOWED_TEXT[name]:
                    errors.append(f"{name} must be one of {sorted(ALLOWED_TEXT[name])}")
                    continue
                self.answers[name] = value
            elif name == "college_name":
                if not isinstance(value, str) or not value.strip():
                    errors.append("college_name must be a non-empty string")
                    continue
                self.answers[name] = value.strip()
            else:
                errors.append(f"Unknown field '{name}'")
        return errors

    def missing_fields(self):
        return [f for f in MODEL_B_FIELDS + PROFILE_FIELDS if f not in self.answers]

    def save(self):
        conn = get_db()
        conn.execute(
            "UPDATE interviews SET messages = ?, answers = ? WHERE id = ?",
            (json.dumps(self.messages), json.dumps(self.answers), self.id),
        )
        conn.commit()

    def complete(self, predictor):
        """Score the finished interview with Model B and store the result (staff-only)."""
        student = Student(**{f: self.answers[f] for f in MODEL_B_FIELDS})
        result = predictor.predict(student)
        self.status = "complete"
        self.risk_score = result["risk_score"]
        self.risk_category = result["risk_category"]
        conn = get_db()
        conn.execute(
            """UPDATE interviews SET status = 'complete', messages = ?, answers = ?, model = ?,
               probability = ?, risk_score = ?, risk_category = ?, completed_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (json.dumps(self.messages), json.dumps(self.answers), result["model"],
             result["probability"], result["risk_score"], result["risk_category"], self.id),
        )
        conn.commit()
        return result

    def override_test_scores(self, predictor, ela_sd=None, math_sd=None):
        """For staff: replace the student's estimated test scores with real ones and re-score."""
        if ela_sd is not None:
            self.answers["ela_sbac_sd_units"] = float(ela_sd)
        if math_sd is not None:
            self.answers["math_sbac_sd_units"] = float(math_sd)
        conn = get_db()
        conn.execute("UPDATE interviews SET test_score_source = 'staff' WHERE id = ?", (self.id,))
        conn.commit()
        self.test_score_source = "staff"
        return self.complete(predictor)

    def transcript(self):
        """The visible chat: student messages and Atlas's text (no tool calls)."""
        lines = []
        for m in self.messages:
            if m["role"] == "user" and isinstance(m["content"], str):
                lines.append({"role": "student", "text": m["content"]})
            elif m["role"] == "assistant":
                text = "\n\n".join(b["text"] for b in m["content"] if b.get("type") == "text")
                if text:
                    lines.append({"role": "atlas", "text": text})
        return lines
