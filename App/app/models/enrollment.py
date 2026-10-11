#Constants definitions

STAGES = ["deciding", "committed", "financial_aid", "registered", "ready"]

TASKS = {"compare_offers":{"label":"Compare your college offers", "stage": "deciding"},
         "review_financial_aid":{"label":"Review financial aid award letters side by side", "stage": "deciding"},
         "visit_schools":{"label":"Visit campuses or attend virtual info sessions if undecided", "stage": "deciding"},
         "final_choice":{"label":"Narrow down schools to a final choice", "stage":"deciding"},
         "accept_offer":{"label":"Formally accept the admission offer in the applicant portal", "stage":"committed"},
         "enrollment_deposit":{"label":"Pay the enrollment deposit (check for a fee waiver if needed)", "stage":"committed"},
         "save_confirmation":{"label":"Save the confirmation receipt", "stage":"committed"},
         "decline_offers":{"label":"Decline other offers you're no longer considering", "stage":"committed"},
         "fafsa":{"label":"Submit the FAFSA (and state/institutional aid forms if required)", "stage":"financial_aid"},
         "review_sar":{"label":"Review your Student Aid Report (SAR) for errors", "stage":"financial_aid"},
         "decide_financial_aid":{"label":"Review and accept/decline each part of your financial aid award (grants, scholarships, work-study, loans)", "stage":"financial_aid"},
         "loan_counseling":{"label":"Complete loan entrance counseling", "stage":"financial_aid"},
         "sign_mpn":{"label":"Sign the Master Promissory Note if taking federal loans", "stage":"financial_aid"},
         "verification_docs":{"label":"Submit any additional financial aid verification documents requested", "stage":"financial_aid"},
         "placement_test":{"label":"Complete placement testing (or confirm excemption via AP/SAT/ACT)", "stage":"registered"},
         "academic_advisor":{"label":"Meet with an academic advisor", "stage":"registered"},
         "course_registration":{"label":"Register for first-semester classes", "stage":"registered"},
         "final_transcript":{"label":"Send your final high school transcript", "stage":"registered"},
         "pre-enrollment_advising":{"label":"Attend mandatory pre-enrollment advising", "stage":"registered"},
         "activate_account":{"label":"Set up and activate your student email/portal account", "stage":"ready"},
         "orientation":{"label":"Register for and attend orientation", "stage":"ready"},
         "health_records":{"label":"Submit immunization/health records", "stage":"ready"},
         "housing":{"label":"Apply for and confirm housing (if applicable)", "stage":"ready"},
         "submit_waivers":{"label":"Submit required wavers/forms (health insurance, FERPA release, etc.)", "stage":"ready"},
         "payment":{"label":"Pay the tuition bill or set up a payment plan", "stage":"ready"},
         "confirm_schedule":{"label":"Confirm your class schedule and locate your classes/campus before day one", "stage":"ready"}}

TASK_COMPLETION = {"compare_offers":{"answer":"compared_offers", "done": 1},
                "review_financial_aid":{"answer":"reviewed_aid", "done": 1},
                "visit_schools":{"answer":"visited_schols", "done": 1},
                "final_choice":{"answer":"decided", "done": 1},
                "accept_offer":{"answer":"accepted_offer", "done": 1},
                "enrollment_deposit":{"answer":"paid_deposit", "done": 1},
                "save_confirmation":{"answer":"confirmation_saved", "done": 1},
                "decline_offers":{"answer":"offers_declined", "done": 1},
                "fafsa":{"answer":"submitted_fafsa_prior_to_graduation", "done": 1},
                "review_sar":{"answer":"sar_reviewed", "done": 1},
                "decide_financial_aid":{"answer":"aid_reviewed", "done": 1},
                "loan_counseling":{"answer":"counseled", "done": 1},
                "sign_mpn":{"answer":"mpn_signed", "done": 1},
                "verification_docs":{"answer":"docs_submitted", "done": 1},
                "placement_test":{"answer":"placed", "done": 1},
                "academic_advisor":{"answer":"advised", "done": 1},
                "course_registration":{"answer":"registered", "done": 1},
                "final_transcript":{"answer":"transcript_sent", "done": 1},
                "pre-enrollment_advising":{"answer":"enrollment_advised", "done": 1},
                "activate_account":{"answer":"account_activated", "done": 1},
                "orientation":{"answer":"oriented", "done": 1},
                "health_records":{"answer":"records_submitted", "done": 1},
                "housing":{"answer":"confirmed", "done": 1},
                "submit_waivers":{"answer":"forms_submitted", "done":1},
                "payment":{"answer":"payment_completed", "done": 1},
                "confirm_schedule":{"answer":"schedule_confirmed", "done": 1}}

#def current_stage function which takes in which tasks you have completed and places you in a stage

def current_stage(answers,tasks):
    for s in STAGES:
        incomplete_tasks=0
        for task in TASKS:
            if TASKS[task]["stage"]==s:
                if not answers.get(TASK_COMPLETION[task]["answer"]) == TASK_COMPLETION[task]["done"] and task not in tasks:
                    incomplete_tasks+=1
        if incomplete_tasks:
            return s
    if not incomplete_tasks:
        return "ready"