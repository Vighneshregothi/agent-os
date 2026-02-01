import os 
import time 
import secrets

class KeyVault:
    def __init__(self):
        self._keys={
            "gemini":os.getenv("GEMINI_API_KEY")
        }

        if not self._keys["gemini"]:
            raise Exception("GEMINI_API_KEY not set in environment ")

class TokenIssuer:
    def __init__(self):
        # token -> metadata
        self._tokens = {}

    def issue_token(self, agent_id: str, action: str, ttl_seconds: int = 300) -> str:
        token = secrets.token_hex(16)  # random, unguessable string
        expires_at = time.time() + ttl_seconds

        self._tokens[token] = {
            "agent_id": agent_id,
            "action": action,
            "expires_at": expires_at
        }

        return token
    
    def validate_token(self,token:str,agent_id:str,action:str)->bool:
        if token not in self._tokens:
            return False
        
        data=self._tokens[token]

        if data["agent_id"] != agent_id:
          return False
        
        if data["action"] != action:
            return False
        
        if time.time()>data["expires_at"]:
            return False
        
        return True
if __name__ == "__main__":
    issuer = TokenIssuer()

    token = issuer.issue_token(
        agent_id="agent_1",
        action="summarize",
        ttl_seconds=10
    )

    print("TOKEN:", token)

    ok = issuer.validate_token(
        token=token,
        agent_id="agent_1",
        action="summarize"
    )

    print("VALID:", ok)
