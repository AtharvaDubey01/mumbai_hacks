import asyncio
from unittest.mock import patch, MagicMock
from app.agents.verifier import verify_claim_text

# Mock responses for the "Trinity" agents
MOCK_DECOMPOSE_RESP = {
    "choices": [{
        "message": {
            "content": '{"queries": ["Is Elon Musk a human?", "Elon Musk alien conspiracy theory origin"]}'
        }
    }]
}

MOCK_VERIFY_RESP = {
    "choices": [{
        "message": {
            "content": '{"verdict": "FALSE", "confidence": 0.95, "summary": "Elon Musk is a human entrepreneur born in Pretoria, South Africa. The \'alien\' claims are part of internet memes and conspiracy theories, often referenced jokingly by Musk himself. There is no biological evidence to support him being extraterrestrial."}'
        }
    }]
}

async def run_mock_test():
    print("Running Robustness Test (with Mocked LLM)...\n")
    
    # Patch the aiohttp.ClientSession.post to return our mock responses
    with patch('aiohttp.ClientSession.post') as mock_post:
        # Setup the mock to return different responses based on the prompt
        async def async_json_side_effect():
            # Simple state machine to return decompose then verify
            if not hasattr(async_json_side_effect, 'call_count'):
                async_json_side_effect.call_count = 0
            
            resp = [MOCK_DECOMPOSE_RESP, MOCK_VERIFY_RESP][async_json_side_effect.call_count]
            async_json_side_effect.call_count += 1
            return resp

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.json.side_effect = async_json_side_effect
        mock_resp.__aenter__.return_value = mock_resp
        mock_post.return_value = mock_resp
        
        claim = "Elon Musk is alien?"
        print(f"Claim: {claim}")
        
        # We also need to mock settings.OPENAI_API_KEY to be truthy so it tries to call the LLM
        with patch('app.config.settings.OPENAI_API_KEY', 'sk-mock-key'):
            result = await verify_claim_text(claim)
            
            print("\n--- Result (Simulated) ---")
            print(f"Verdict: {result['verdict']}")
            print(f"Score: {result['score']}")
            print(f"Summary: {result['summary']}")
            print(f"Evidence Count: {len(result['evidence'])}")

if __name__ == "__main__":
    asyncio.run(run_mock_test())
