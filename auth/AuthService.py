import httpx
from fastapi import HTTPException, Header
from typing import Optional


class AuthService:
    def __init__(self, introspect_url: str):
        self.introspect_url = introspect_url

    async def verify_token(self, authorization: Optional[str] = Header(None)) -> dict:
        """
        Verify the authorization token by calling the introspect endpoint

        Args:
            authorization: Authorization header value (e.g., "Bearer <token>")

        Returns:
            dict: Token introspection response

        Raises:
            HTTPException: If token is missing, invalid, or introspection fails
        """

        print(authorization)
        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Authorization header is missing",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Extract token from "Bearer <token>"
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header format. Expected: Bearer <token>",
                headers={"WWW-Authenticate": "Bearer"}
            )

        token = parts[1]

        try:
            # Call introspect endpoint
            print(self.introspect_url)
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.introspect_url,
                    headers={
                             "Authorization": f"Bearer {token}",
                             }

                )
                print(response.json())
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=401,
                        detail=f"Token introspection failed: {response.text}",
                        headers={"WWW-Authenticate": "Bearer"}
                    )

                introspect_data = response.json()

                # Check if token is active
                if not introspect_data.get("active", False):
                    raise HTTPException(
                        status_code=401,
                        detail="Token is not active or has expired",
                        headers={"WWW-Authenticate": "Bearer"}
                    )

                return introspect_data

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to connect to introspection service: {str(e)}"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Token verification failed: {str(e)}"
            )
