# Keycloak Integration

This repo contains a sample flask app which interacts with keycloak server over the APIs

```
# information retrieved from keycloak server looks like this
{
  "access_token_info": {
    "acr": "0",
    "aud": "account",
    "auth_time": 1553445172,
    "azp": "flask-app",
    "email": "akhil.lawrence@lntinfotech.com",
    "email_verified": true,
    "exp": 1553445641,
    "family_name": "Lawrence",
    "given_name": "Akhil",
    "iat": 1553445341,
    "iss": "https://keycloak.dev.lti-mosaic.com/auth/realms/akhil-poc",
    "jti": "868b94c4-a97e-4b7d-af53-59d9b970ea55",
    "name": "Akhil Lawrence",
    "nbf": 0,
    "preferred_username": "akhil.lawrence",
    "resource_access": {
      "account": {
        "roles": [
          "manage-account",
          "manage-account-links",
          "view-profile"
        ]
      },
      "flask-app": {
        "roles": [
          "Administrator",
          "AppUser"
        ]
      }
    },
    "scope": "openid profile user_roles email",
    "session_state": "870c5d0b-1b0c-4d9b-801a-1e1637c8dabc",
    "sub": "71da70b2-f922-4e98-a9a1-4e2c13510663",
    "typ": "Bearer"
  },
  "id_token_info": {
    "acr": "0",
    "aud": "flask-app",
    "auth_time": 1553445172,
    "azp": "flask-app",
    "email": "akhil.lawrence@lntinfotech.com",
    "email_verified": true,
    "exp": 1553445641,
    "family_name": "Lawrence",
    "given_name": "Akhil",
    "iat": 1553445341,
    "iss": "https://keycloak.dev.lti-mosaic.com/auth/realms/akhil-poc",
    "jti": "1f0fa155-8d61-436d-bf47-a5df1c5ce7d7",
    "name": "Akhil Lawrence",
    "nbf": 0,
    "preferred_username": "akhil.lawrence",
    "session_state": "870c5d0b-1b0c-4d9b-801a-1e1637c8dabc",
    "sub": "71da70b2-f922-4e98-a9a1-4e2c13510663",
    "typ": "ID"
  }
}
```
