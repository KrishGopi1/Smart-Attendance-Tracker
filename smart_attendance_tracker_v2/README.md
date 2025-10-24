Smart Attendance Tracker

Setup:
1. Install dependencies: pip install -r requirements.txt
2. Copy .env.example to .env and fill values.
3. Create MySQL database and update DATABASE_URL in .env.
4. Run: python run.py
5. Seed sample data: python seed_students.py

Features:
- Teacher login (simple username/password from env, default 'teacher'/'password')
- Teacher dashboard with class list and checkbox attendance UI
- Bulk attendance insert and optimized queries
- Twilio SMS alerts for absentees (reads credentials from env)
