FutureBound Philly

**How to Run:**

**Prerequisites**
Python 3.12
A Google Cloud OAuth 2.0 client ID and secret for a Web application
An Anthropic API key for Atlas, the AI college counselor
Configure this authorized redirect URI in your Google OAuth client: http://localhost:5001/auth/callback

**Installation**
1. Clone the repository and navigate to the application directory.
git clone https://github.com/margocodez/FutureBoundPhilly.git
cd FutureBoundPhilly/App
2. Create and activate a virtual environment.
python3 -m venv .venv
source .venv/bin/activate
3. Install dependencies.
pip install -r requirements.txt
4. Configure environment variables.
Create your local environment file:
cp .env.example .env
Open .env and configure the following variables:
SECRET_KEY: A securely generated random secret for Flask.
GOOGLE_CLIENT_ID: Your Google OAuth client ID.
GOOGLE_CLIENT_SECRET: Your Google OAuth client secret.
ANTHROPIC_API_KEY: Your Anthropic API key for Atlas.
STAFF_EMAILS: Google email address(es) authorized to access the staff dashboard.
MENTOR_EMAILS: Optional email address(es) for mentor access.
MAIL_USERNAME: Optional email account for sending reminders.
MAIL_PASSWORD: Optional email account password or app password.
Keep .env private. Never commit API keys, OAuth secrets, or other credentials to GitHub. If email credentials are not configured, reminder emails are printed to the terminal instead.
6. Start the application.
Run the app on port 5001 to match the Google OAuth redirect URI:
PORT=5001 python run.py
7. Open the application.
Navigate to http://localhost:5001 in your browser and sign in with Google.

**Additional Notes**
Database: The SQLite database initializes automatically on the first run; no manual setup is required.
Machine learning: The trained Model B files are included in FBP_NN/, so you do not need to retrain the model.
Credentials: You must configure your own Google OAuth credentials and Anthropic API key before running the app.
Security: Ensure .env is excluded by .gitignore and never publish private credentials.

FutureBound Philly is designed to support students without treating an experimental risk score as a judgment about their potential.

- Atlas safety rules: The support prompt includes boundaries intended to keep conversations focused on college enrollment, provide appropriate guidance, and avoid unsupported promises about admissions or financial aid.
- Message limit: Atlas has a limit of 50 messages per user per day to help manage usage and costs.
- Access control: Student, mentor, and staff functionality is separated by user roles.
- Checklist ownership: Students should only be able to modify their own checklist tasks.
- API key handling: The app stores scrambled/hash-based copies of access keys rather than retaining the original keys in readable form.
- Secret management: Credentials and private configuration belong in `.env`, not in version control.
- Student data: Real student records and other sensitive data should not be committed to Git. The machine-learning training dataset is simulated, not a dataset of 100,000 actual students.
- Model limitations: Risk predictions are experimental and should not be used as the sole basis for decisions about students or access to resources.

These safeguards reflect the project's intended design. Any real-world pilot would require additional review of privacy, security, consent, and access controls.

Future Plans: FutureBound Philly 2.0

Planned improvements include:

- Scheduled and text-message reminders: Automate reminders and offer optional SMS notifications with student consent.
- College-specific deadlines: Personalize checklists with verified deadlines for institutions such as Temple University, the Community College of Philadelphia, and Drexel University.
- Stronger mentor follow-ups: Track mentor check-ins and checklist progress, with alerts when students may need additional support.
- Improved model evaluation: Use appropriate real-world data with consent and safeguards, improve calibration, and provide clearer explanations of predictions.
- More capable Atlas interactions: Allow Atlas to propose checklist updates or new tasks, with student confirmation before changes are made.
- Calendar integration: Let students export enrollment deadlines to their personal calendars.
- Online deployment and consent: Add a clear consent process and privacy information to support a carefully evaluated pilot with real students.
- Reliable email delivery: Configure and test production-ready email delivery rather than relying on a staff-triggered process or development fallback.

The long-term goal is to evaluate whether FutureBound Philly can help students complete enrollment requirements on time and improve college matriculation outcomes.

AI Use Disclosure

I used Claude, Anthropic's AI assistant, through Claude Code as a coding aid while building portions of FutureBound Philly.

What Claude Wrote or Helped Implement

- Initial app framework: Claude wrote parts of the first Flask application version before October 4, 2026, including app setup and configuration, Google sign-in, the Atlas interview system, the developer API and access-key functionality, and initial versions of several templates and the stylesheet.
- Atlas support prompt edits: Claude edited specific sections concerning AI transparency, FAFSA and family income, safety, and the current date. I wrote the rest of the support prompt.
- Reminder feature: Claude wrote the staff route for sending due-soon reminders, the reminder button and confirmation message, two CSS rules, and a fix to the checklist link in `reminders.py`. The corresponding commit identifies Claude as a co-author.
- Synthetic data set: Formed based on SAGE published summer melt research and findings from the School district of Philadelhpia. 100,000 simulated students created to train Model A and Model B

What I Wrote

- The machine-learning training scripts and Model A and Model B (the one actually used on students in the app) in `FBP_NN/`
- The enrollment stages
- The personalized checklist, task pages, and task-completion functionality
- The Atlas support chat and most of its support prompt
- The staff dashboard
- Mentor requests, mentor assignments, and the My Students page
- The homepage and its design
- Most of the reminder email feature
- The risk-score cutoffs and stage-name display

Claude contributed to specific parts of the code, but I developed the machine-learning models and implemented the majority of the application's features myself. This disclosure is intended to accurately represent how AI assisted in the development process.
Claude was not used in any way for the development of the concept of this application.

Acknowledgments and Research

FutureBound Philly's design was informed by research on summer melt and college enrollment barriers, including:

- [School District of Philadelphia: Summer Melt — Results from the Classes of 2022, 2023, and 2024](https://www.philasd.org/research/2025/07/31/summer-melt-how-many-seniors-follow-through-on-plans-to-attend-college-results-from-the-senior-classes-of-2022-2023-and-2024/)
- "Leaks in the College Access Pipeline: Examining Summer Melt in a Large Urban School District" - Research on summer melt and enrollment support, including work published through SAGE Journals.

Research informs the platform's design, but the app's model accuracy and its impact on actual college enrollment still need to be evaluated.
