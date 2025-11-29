import asyncio
from app.agents.verifier import verify_claim_text
from app.config import settings

async def main():
    print(f"Testing with OpenAI Key: {settings.OPENAI_API_KEY[:5]}..." if settings.OPENAI_API_KEY else "No OpenAI Key")
    
    claim = "youth of india is unemployed?"
    print(f"\nVerifying claim: {claim}")
    result = await verify_claim_text(claim)
    
    print("\n--- Result ---")
    print(f"Verdict: {result['verdict']}")
    print(f"Score: {result['score']}")
    print(f"Summary: {result['summary']}")
    print("\nEvidence Sources:")
    for e in result['evidence']:
        print(f"- {e.get('source')}: {e.get('title')}")

if __name__ == "__main__":
    asyncio.run(main())
