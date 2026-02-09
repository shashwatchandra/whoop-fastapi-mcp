# Agera × WHOOP (FastAPI)

## Prerequisites
- Python 3.10+
- VS Code with Python extension
- HTTPS dev URL (ngrok/cloudflared) for OAuth redirect

## Quick Start

1. **Open the folder in VS Code**

2. **Create a virtual env and install deps:**
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate
   # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Copy env template and edit:**
   ```bash
   cp .env.example .env
   ```
   - Set `WHOOP_CLIENT_ID` to your value
   - Set `WHOOP_CLIENT_SECRET` to your value
   - Set `PUBLIC_BASE_URL` to your HTTPS tunnel (e.g., `https://abc123.ngrok-free.dev`)

4. **Start ngrok tunnel:**
   ```bash
   ngrok http 3000
   ```
   Copy the ngrok URL and update `PUBLIC_BASE_URL` in `.env`

5. **In the WHOOP Developer Console, set Redirect URL to:**
   ```
   https://<your-ngrok-url>/callback
   ```

6. **Run the application:**
   ```bash
   python whoop_simple.py
   ```

7. **Complete OAuth:**
   - Open `http://localhost:3000` in your browser
   - Click "Click here to login with WHOOP"
   - Authorize the application

8. **Try the endpoints:**
   - `/profile` — profile + body measurements + recent cycles
   - `/cycles?start=YYYY-MM-DD&end=YYYY-MM-DD` — cycles data with optional date range
   - `/workouts?start=YYYY-MM-DD&end=YYYY-MM-DD` — workouts with optional date range
   - `/sleep?start=YYYY-MM-DD&end=YYYY-MM-DD` — sleep data with optional date range

## Important Notes

- **API Base URL**: Use `https://api.prod.whoop.com/developer/v1/` (not `/v1/` or `/v2/`)
- **State Parameter**: Must be at least 8 characters long
- **OAuth Callback**: Requires HTTPS (hence ngrok requirement)
- **Scopes**: Currently using `read:profile` and `read:body_measurement`

## Troubleshooting

- **404 errors**: Ensure you're using the `/developer/v1/` API base
- **State validation failed**: Check that your state parameter is 8+ characters
- **OAuth callback fails**: Verify ngrok is running and `PUBLIC_BASE_URL` matches
- **No data returned**: Check scopes in WHOOP app settings
