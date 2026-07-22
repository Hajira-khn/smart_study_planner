# Smart Study Planner — Web Version

Flask rewrite of the original Tkinter desktop app, ready to deploy on Vercel.
All business logic is untouched — it's still the same `logic.py` from the
original repo (same 69 tests, all still passing).

## Run locally
```
pip install -r requirements.txt
python app.py
```
Visit http://127.0.0.1:5000

## Deploy to Vercel
1. Push this folder to a GitHub repo (or a new branch of your existing one).
2. Go to https://vercel.com/new and import the repo.
3. Vercel will detect `vercel.json` and deploy automatically — no config needed.
4. (Optional) Set an environment variable `SECRET_KEY` to a random string in
   the Vercel project settings, for signing session cookies in production.

## Notes
- Data (subjects, study sessions) is stored in the browser session cookie —
  there's no database. This matches a demo/portfolio app; if you want data to
  persist across devices/sessions, the next step would be adding a small
  database (e.g. Vercel Postgres or Supabase).
- The subject dropdown in the planner uses the fixed list from `logic.py`
  (Programming, AI, HCI, English, Mathematics), same as the original app.
  Subjects added on the Subjects page are a separate, freely-named list.
