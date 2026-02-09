# WHOOP OAuth - Simple Setup

## Quick Start

1. **Make sure `.env` is configured:**
   ```
   WHOOP_CLIENT_ID=e59d4fb0-96e9-4f45-96a9-04c6185e1dce
   WHOOP_CLIENT_SECRET=821332898021f08f0cd5f90009767f3f8a784d1ce32828e0de9eaa28e706a254
   PUBLIC_BASE_URL=https://hyponastically-electronegative-angelita.ngrok-free.dev
   SESSION_SECRET=change_this_random_string
   ```

2. **Start ngrok** (in a separate terminal, leave it running):
   ```powershell
   ngrok http 3000
   ```

3. **Start the server** (in another terminal):
   ```powershell
   & .venv\Scripts\python.exe simple_app.py
   ```

4. **Visit**:
   ```
   https://hyponastically-electronegative-angelita.ngrok-free.dev/login
   ```

5. **After OAuth**, you'll be redirected to `/profile` with your WHOOP data

## Available Endpoints

- `/login` - Start OAuth flow
- `/profile` - Your profile + body measurements  
- `/cycles?start=2026-01-01T00:00:00Z&end=2026-02-01T00:00:00Z` - Cycles data
- `/workouts?start=2026-01-01T00:00:00Z&end=2026-02-01T00:00:00Z` - Workouts data

## Troubleshooting

If you get "Internal Server Error":
1. Check that the server is actually running (`python simple_app.py`)
2. Check that ngrok is forwarding to port 3000
3. Look at the terminal where `simple_app.py` is running for error messages
4. Make sure your WHOOP Developer Console has the callback URL set to:
   `https://hyponastically-electronegative-angelita.ngrok-free.dev/callback`
