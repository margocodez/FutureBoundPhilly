#Constants definitions

STAGES = ["deciding", "committed", "financial_aid", "registered", "ready"]

#def current_stage function which takes in which tasks you have completed and places you in a stage

def current_stage(tasks):
    for s in STAGES:
        incomplete_tasks=0
        for row in tasks:
            if row["stage"]==s:
                if row["status"] != "done":
                    incomplete_tasks+=1
        if incomplete_tasks:
            return s
    if not incomplete_tasks:
        return "ready"