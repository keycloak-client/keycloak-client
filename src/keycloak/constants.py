# -*- coding: utf-8 -*-


class Logger:
    """ constants associated with logger """

    name = "keycloak"


class Defaults:
    """ constants associated with default values """

    keycloak_settings = "keycloak.json"


class EnvVar:
    """ constants associated with env vars """

    keycloak_settings = "KEYCLOAK_SETTINGS"


class FileMode:
    """ constants associated with file mode """

    read_only = "r"


class TokenType:
    """ constants associated with token types """

    basic = "Basic"
    bearer = "Bearer"


class Headers:
    """ constants associated with headers """

    authorization = "Authorization"


class GrantTypes:
    """ constants associated with grant types """

    password = "password"
    authorization_code = "authorization_code"
    client_credentials = "client_credentials"
    uma_ticket = "urn:ietf:params:oauth:grant-type:uma-ticket"


class ResponseTypes:
    """ constants associated with response types """

    code = "code"


class TokenTypeHints:
    """ constants associated with token type hints """

    rpt = "requesting_party_token"


class Algorithms:
    """ constants associated with algorithms """

    ec = ("ES256", "ES384", "ES521", "ES512")
    hmac = ("HS256", "HS384", "HS512")
    rsa = ("RS256", "RS384", "RS512")
    rsapss = ("PS256", "PS384", "PS512")
