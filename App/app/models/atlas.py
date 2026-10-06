import anthropic

MODEL = "claude-opus-5-5"
FALLBACK_BETA = "server-side-fallback-2026-07-01"
MAX_TOOL_ROUNDS = 5


def greeting(first_name):
    name = f" {first_name}" if first_name else ""
    return (f"Hi{name}! I'm Atlas, your college enrollment counselor. I'd like to ask you a few "
            "quick questions about high school and your college plans so we can build your "
            "enrollment plan. It takes about 5 minutes. Ready to get started?")


SYSTEM_PROMPT = """You are Atlas, a warm, encouraging college enrollment counselor for Future Bound Philly, \
a Philadelphia program that helps students who plan to go to college actually enroll in the fall. \
You're talking with a high school senior or recent graduate in a short chat interview. The student \
has already seen your greeting, which said you'd ask a few quick questions to build their enrollment plan.

Your job is to learn the 20 facts below (13 about high school, 7 about their college plans), in a natural conversation, and save them with the \
record_answers tool. Ask one question at a time in plain, friendly language a 17-year-old would use, \
and keep each message to a sentence or two. You can save answers as you go -- call record_answers \
whenever you've learned one or more facts. If an answer is vague, ask a quick follow-up rather than \
guessing; if the student genuinely doesn't know, pick the closest reasonable value.

Facts to collect (tool field: meaning):
- submitted_fafsa_prior_to_graduation: have they submitted the FAFSA (before graduating, if they've \
graduated)? 1 = yes, 0 = no
- self_reported_attendance: how often they missed school. 0 = frequently, 1 = sometimes, 2 = rarely
- very_certain_attend_planned_college: are they very certain they'll attend the college they plan \
to? 1 = very certain, 0 = less than very certain
- planned_enrollment_intensity: 0 = part time, 1 = unsure, 2 = full time
- unsure_what_semester_start: 1 = unsure which semester they're starting, 0 = knows
- concurrent_cc_enrollment: took community college classes (dual enrollment) during high school? \
1 = yes, 0 = no
- registered_cc_prior_to_graduation: registered at a two-year/community college before graduating? \
1 = yes, 0 = no
- parent_education: highest education of either parent/guardian. 0 = less than high school, \
1 = high school graduate, 2 = some college, 3 = bachelor's degree, 4 = graduate degree
- cumulative_gpa: high school GPA, 0.0 to 4.3 (an estimate is fine)
- ela_test_level / math_test_level: how they did on state standardized tests in English/reading and \
in math (in Pennsylvania, the Keystone exams or PSSA). One of below_basic, basic, proficient, \
advanced, or unknown if they don't remember
- passed_ap_ib_course: passed at least one AP or IB class? 1 = yes, 0 = no
- passed_ap_ib_exam: passed at least one AP or IB exam? 1 = yes, 0 = no (if they took no AP/IB \
classes, this is 0 -- don't ask)

College plan facts (used to build the student's enrollment checklist):
- college_name: the name of the college or school they plan to attend
- school_type: trade (trade/technical school), 2_year (community college), 4_year, or unsure
- starting_term: fall, spring, or unsure
- living_on_campus: yes, no, or unsure
- accepted: have they been accepted? 1 = yes, 0 = no (not yet, or still waiting)
- accepted_offer: have they officially accepted the school's offer? 1 = yes, 0 = no (if \
accepted is 0, this is 0 -- don't ask)
- paid_deposit: have they paid the enrollment deposit? 1 = yes, 0 = no (if accepted is 0, this \
is 0 -- don't ask; if the school has no deposit, as many community colleges don't, record 1)

Some facts overlap, so don't ask the same thing twice:
- starting_term and unsure_what_semester_start come from one question: if starting_term is \
unsure, unsure_what_semester_start is 1; otherwise it's 0.
- If school_type is 2_year and they've already registered there, registered_cc_prior_to_graduation \
is 1; ask only if it isn't clear.
- Once you know the college, ask about living on campus only if it makes sense (most community \
college students live at home, but confirm briefly).

Guidelines:
- Don't ask about race, ethnicity, gender, disability, special education, English-learner status, \
or family income. If the student brings these up, respond kindly without recording them.
- Never mention risk, scores, predictions, models, or "summer melt". From the student's point of \
view, you're gathering information for their enrollment plan.
- It's fine to briefly answer a student's question (e.g., what the FAFSA is) before moving on. \
Don't promise specific financial aid amounts or admissions outcomes.
- If a student shares something concerning about their safety or wellbeing, respond with care and \
encourage them to talk with their school counselor or a trusted adult; in an emergency, call 911 \
or text/call 988.
- When every fact is saved, thank the student in one or two sentences and tell them you're putting \
together their enrollment plan, then call complete_interview in that same turn."""


_BINARY = {"type": "integer", "enum": [0, 1]}
_LEVEL = {"type": "string", "enum": ["below_basic", "basic", "proficient", "advanced", "unknown"]}

TOOLS = [
    {
        "name": "record_answers",
        "description": "Save one or more of the student's answers. Include only fields you've "
                       "learned; you can call this several times during the interview. Returns "
                       "the fields still missing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "submitted_fafsa_prior_to_graduation": _BINARY,
                "self_reported_attendance": {"type": "integer", "enum": [0, 1, 2]},
                "very_certain_attend_planned_college": _BINARY,
                "planned_enrollment_intensity": {"type": "integer", "enum": [0, 1, 2]},
                "unsure_what_semester_start": _BINARY,
                "concurrent_cc_enrollment": _BINARY,
                "registered_cc_prior_to_graduation": _BINARY,
                "parent_education": {"type": "integer", "enum": [0, 1, 2, 3, 4]},
                "cumulative_gpa": {"type": "number", "minimum": 0, "maximum": 4.3},
                "ela_test_level": _LEVEL,
                "math_test_level": _LEVEL,
                "passed_ap_ib_course": _BINARY,
                "passed_ap_ib_exam": _BINARY,
                "college_name": {"type": "string", "minLength": 1},
                "school_type": {"type": "string", "enum": ["trade", "2_year", "4_year", "unsure"]},
                "starting_term": {"type": "string", "enum": ["fall", "spring", "unsure"]},
                "living_on_campus": {"type": "string", "enum": ["yes", "no", "unsure"]},
                "accepted": _BINARY,
                "accepted_offer": _BINARY,
                "paid_deposit": _BINARY,
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "complete_interview",
        "description": "Finish the interview once every fact has been saved. Fails and lists "
                       "the missing fields if anything is still unanswered.",
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
]

REFUSAL_REPLY = "Sorry, I can't help with that one. Could you say it another way?"
ERROR_REPLY = "Sorry, I'm having trouble connecting right now. Please try sending that again."


def _call_claude(client, system, messages):
    return client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=system,
        tools=TOOLS,
        messages=messages,
        output_config={"effort": "low"},  # short conversational turns
        cache_control={"type": "ephemeral"},
        betas=[FALLBACK_BETA],
        fallbacks="default",
    )


def run_turn(interview, student_text, first_name, client=None):
    """Send the student's message to Atlas and handle any tool calls.

    Returns {"replies": [str], "done": bool}. The interview's messages/answers are
    updated in place only if the turn succeeds; the caller saves them.
    """
    client = client or anthropic.Anthropic()
    system = SYSTEM_PROMPT + (f"\n\nThe student's first name is {first_name}." if first_name else "")

    messages = list(interview.messages)
    answers = dict(interview.answers)
    messages.append({"role": "user", "content": student_text})
    replies, done = [], False

    try:
        for _ in range(MAX_TOOL_ROUNDS):
            response = _call_claude(client, system, messages)
            if response.stop_reason == "refusal":
                interview.answers = answers  # discard this turn entirely
                return {"replies": [REFUSAL_REPLY], "done": False}

            messages.append({"role": "assistant", "content": response.to_dict()["content"]})
            replies += [b.text for b in response.content if b.type == "text" and b.text.strip()]

            tool_uses = [b for b in response.content if b.type == "tool_use"]
            if not tool_uses:
                break

            results = []
            for tool_use in tool_uses:
                content, is_error = _run_tool(interview, tool_use)
                if tool_use.name == "complete_interview" and not is_error:
                    done = True
                results.append({"type": "tool_result", "tool_use_id": tool_use.id,
                                "content": content, "is_error": is_error})
            messages.append({"role": "user", "content": results})
            if done:
                break
    except anthropic.APIError:
        interview.answers = answers
        return {"replies": [ERROR_REPLY], "done": False}

    interview.messages = messages
    return {"replies": replies, "done": done}


def _run_tool(interview, tool_use):
    if tool_use.name == "record_answers":
        errors = interview.record_answers(tool_use.input or {})
        missing = interview.missing_fields()
        status = f"Still missing: {', '.join(missing)}." if missing else "All facts collected."
        if errors:
            return "Some answers were not saved: " + "; ".join(errors) + ". " + status, True
        return "Saved. " + status, False

    if tool_use.name == "complete_interview":
        missing = interview.missing_fields()
        if missing:
            return f"Can't finish yet. Still missing: {', '.join(missing)}.", True
        return "Interview saved.", False

    return f"Unknown tool '{tool_use.name}'", True
