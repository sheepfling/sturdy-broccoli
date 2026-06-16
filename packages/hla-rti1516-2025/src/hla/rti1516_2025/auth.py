"""Authorization protocols for IEEE 1516.1-2025.

Sources: Java hla/rti1516_2025/auth/*.java and C++ RTI/auth/*.h.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Protocol, runtime_checkable

from .datatypes import Credentials
from .enums import AuthorizationResultCode


@dataclass(frozen=True, slots=True)
class AuthorizationResult:
    code: AuthorizationResultCode
    message: str = ""

    def getCode(self) -> AuthorizationResultCode:
        return self.code

    def getMessage(self) -> str:
        return self.message


@runtime_checkable
class Authorizer(Protocol):
    def authorizeRtiOperation(self, credentials: Credentials) -> AuthorizationResult: ...

    def authorizeFederationOperation(
        self, credentials: Credentials, federationName: str
    ) -> AuthorizationResult: ...

    def authorizeFederateOperation(
        self,
        credentials: Credentials,
        federationName: str,
        federateName: str,
        federateType: str,
    ) -> AuthorizationResult: ...

    def getName(self) -> str: ...


@runtime_checkable
class AuthorizerFactory(Protocol):
    HLA_AUTHORIZER_NAME: ClassVar[str]

    def getName(self) -> str: ...

    def getAuthorizer(self) -> Authorizer: ...


@runtime_checkable
class AuthorizerFactoryFactory(Protocol):
    @staticmethod
    def getAuthorizerFactory(authorizerName: str) -> AuthorizerFactory | None: ...


class HLAnoCredentials(Credentials):
    HLA_NO_CREDENTIALS_TYPE: ClassVar[str] = "HLAnoCredentials"

    def __new__(cls):
        return super(HLAnoCredentials, cls).__new__(
            cls, cls.HLA_NO_CREDENTIALS_TYPE, b""
        )


class HLAplainTextPassword(Credentials):
    HLA_PLAIN_TEXT_PASSWORD_TYPE: ClassVar[str] = "HLAplainTextPassword"

    def __new__(cls, password_or_data: str | bytes):
        data = (
            cls.encode(password_or_data)
            if isinstance(password_or_data, str)
            else bytes(password_or_data)
        )
        return super(HLAplainTextPassword, cls).__new__(
            cls, cls.HLA_PLAIN_TEXT_PASSWORD_TYPE, data
        )

    @staticmethod
    def encode(password: str) -> bytes:
        """Encode as Java/C++ HLAplainTextPassword: length + UTF-16 code units."""
        body = bytearray()
        for ch in password:
            value = ord(ch)
            body.append((value >> 8) & 0xFF)
            body.append(value & 0xFF)
        return len(password).to_bytes(4, "big", signed=False) + bytes(body)

    def decode(self) -> str:
        if len(self.data) < 4:
            raise ValueError("Encoded HLAplainTextPassword is too short")
        count = int.from_bytes(self.data[:4], "big", signed=False)
        body = self.data[4:]
        if len(body) < count * 2:
            raise ValueError("Encoded HLAplainTextPassword is truncated")
        return "".join(
            chr((body[i] << 8) | body[i + 1]) for i in range(0, count * 2, 2)
        )
