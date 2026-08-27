import asyncio
import httpx
import random

SIMULATED_POSTS = [
    {"platform": "X/Twitter", "content": "Large violent crowd throwing rocks and rioting near Main Station! Police barricades broken."},
    {"platform": "Telegram", "content": "Massive fire and explosions heard near South Gate industrial zone, send ambulances fast!"},
    {"platform": "Reddit", "content": "Traffic is moving very slow on 5th Avenue today due to rain, stay safe."},
    {"platform": "X/Twitter", "content": "Armed mob clashing with security near City Center! Gunshots reported!"},
    {"platform": "Telegram", "content": "Just had coffee downtown, weather is peaceful."},
    {"platform": "Reddit", "content": "Critical situation: building collapse and looting reported near Metro Station."}
]

async def run_osint_feed_simulation(api_url: str = "http://127.0.0.1:8000/api/v1/osint/threat-scanner", interval_seconds: int = 6):
    """Periodically post mock social signals to the live threat scanner."""
    async with httpx.AsyncClient() as client:
        while True:
            post = random.choice(SIMULATED_POSTS)
            try:
                response = await client.post(api_url, json=post, timeout=10.0)
                result = response.json()
                print(f"[SIMULATOR] Ingested [{post['platform']}]: '{post['content'][:45]}...' -> Escalated: {result.get('escalated_to_incident')}")
            except Exception as e:
                print(f"[SIMULATOR WARNING] Ingestion failed: {e}")
            await asyncio.sleep(interval_seconds)

if __name__ == "__main__":
    print("Starting automated OSINT social stream simulator (Ctrl+C to stop)...")
    asyncio.run(run_osint_feed_simulation())
