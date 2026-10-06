from dataclasses import dataclass, fields


@dataclass
class Student:
    """One student's inputs. Field names match the CSV / feature-order columns."""

    submitted_fafsa_prior_to_graduation: int = 0
    self_reported_attendance: int = 0
    very_certain_attend_planned_college: int = 0
    planned_enrollment_intensity: int = 0
    unsure_what_semester_start: int = 0
    concurrent_cc_enrollment: int = 0
    registered_cc_prior_to_graduation: int = 0
    intended_college_type: int = 4
    female: int = 0
    is_asian: int = 0
    is_black: int = 0
    is_hispanic_latine: int = 0
    is_white: int = 0
    is_multiracial_other: int = 0
    english_learner_status: int = 0
    special_education_iep: int = 0
    economically_disadvantaged: int = 0
    parent_education: int = 0
    cumulative_gpa: float = 0.0
    ela_sbac_sd_units: float = 0.0
    math_sbac_sd_units: float = 0.0
    passed_ap_ib_course: int = 0
    passed_ap_ib_exam: int = 0

    @classmethod
    def field_names(cls):
        return [f.name for f in fields(cls)]

    @classmethod
    def from_dict(cls, data):
        """Build a Student from JSON; missing fields keep their defaults.

        Raises ValueError naming the field if a value can't be converted.
        """
        values = {}
        for f in fields(cls):
            raw = data.get(f.name)
            if raw in (None, ""):
                continue
            try:
                values[f.name] = f.type(float(raw)) if f.type is int else f.type(raw)
            except (TypeError, ValueError):
                raise ValueError(f"Invalid value for '{f.name}': {raw!r}")
        return cls(**values)
