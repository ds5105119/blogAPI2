from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from typing import Optional
from uuid import uuid4

from jose import JWTError, jwt
from jose.constants import ALGORITHMS


class AbstractJWTManager(ABC):
    """
    Abstract base class for managing JSON Web Tokens (JWT).
    This class defines the interface for encoding and decoding JWTs.
    """

    @abstractmethod
    def encode(self, claims: dict, expires_delta: int, secret_key: str, algorithm: str) -> str:
        """
        Encodes the specified claims into a JSON Web Token (JWT).

        :param claims: A dictionary containing the claims to be included in the JWT.
        :param expires_delta: The expiration time in seconds for the JWT.
        :param secret_key: The secret key used to sign the JWT.
        :param algorithm: The signing algorithm to be used for the JWT.

        :return: A string representation of the encoded JWT.

        :raises NotImplementedError: If this method is not implemented in a subclass.
        """
        raise NotImplementedError("subclasses of JWTEncoder must provide a encode() method")

    @abstractmethod
    def decode(self, token: str, secret_key: str, algorithm: str) -> dict | None:
        """
        Decodes a JSON Web Token (JWT) and validates its claims.

        :param token: The JWT string to be decoded.
        :param secret_key: The secret key used to validate the JWT signature.
        :param algorithm: The signing algorithm used to verify the JWT,

        :return: A dictionary containing the claims if the token is valid,
                 or None if the token is invalid or expired.

        :raises NotImplementedError: If this method is not implemented in a subclass.
        """
        raise NotImplementedError("subclasses of JWTEncoder must provide a decode() method")


class JWT(AbstractJWTManager):
    """
    JWT manager for encoding and decoding JSON Web Tokens.
    """

    def get_jti(self) -> str:
        """
        Generates a unique identifier (JWT ID) for the token.

        :return: JWT ID (jti),
        """
        return uuid4().hex

    def encode(
        self,
        claims: dict,
        expires_delta: int,
        secret_key: str,
        algorithm: str = ALGORITHMS.ES384,
        access_token: Optional[str] = None,
    ) -> str:
        """
        Encodes the specified claims into a JSON Web Token (JWT) with a specified expiration time.
        :param claims: A dictionary containing the claims to be included in the JWT.
        :param expires_delta: The expiration time in seconds for the JWT.
        :param algorithm: The signing algorithm to use for the JWT, defaults to 'ES384'.
        :param access_token: Optional parameter for additional handling of access tokens.

        :return: JWT
        """
        to_encode = claims.copy()

        to_encode.setdefault("exp", datetime.now(UTC) + timedelta(seconds=expires_delta))
        to_encode.setdefault("iat", datetime.now(UTC))
        to_encode.setdefault("jti", self.get_jti())

        return jwt.encode(to_encode, secret_key, algorithm=algorithm, access_token=access_token)

    def decode(
        self, token: str, secret_key: str, algorithm: str = ALGORITHMS.ES384, access_token: Optional[str] = None
    ) -> dict | None:
        """
        Decodes a JSON Web Token (JWT) and returns the claims if valid.

        :param token: The JWT string to be decoded.
        :param secret_key: The secret key used to validate the JWT signature.
        :param algorithm: The signing algorithm used for verification JWT, defaults to 'ES384'.
        :param access_token: Optional parameter for additional handling of access tokens.

        :return: A dictionary containing the claims if the token is valid,
                 or None if the token is invalid or expired.
        """
        try:
            return jwt.decode(token, secret_key, algorithms=[algorithm], access_token=access_token)
        except JWTError:
            return None
