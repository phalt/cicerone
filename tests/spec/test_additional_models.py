"""Tests for additional component models."""

from cicerone import spec


class TestMediaType:
    """Tests for spec.mediatype.MediaType model."""

    def test_media_type_from_dict(self):
        """Test creating spec.mediatype.MediaType from dict."""
        data = {
            "schema": {"type": "object", "properties": {"id": {"type": "string"}}},
            "example": {"id": "123"},
        }
        media_type = MediaType.from_dict(data)
        assert media_type.schema_ == {"type": "object", "properties": {"id": {"type": "string"}}}
        assert media_type.example == {"id": "123"}

    def test_media_type_with_examples(self):
        """Test creating spec.mediatype.MediaType with examples as spec.example.Example objects."""
        data = {
            "schema": {"type": "string"},
            "examples": {
                "user1": {"value": "John", "summary": "First user"},
                "user2": {"value": "Jane"},
            },
        }
        media_type = MediaType.from_dict(data)
        assert "user1" in media_type.examples
        assert "user2" in media_type.examples
        assert isinstance(media_type.examples["user1"], spec.example.Example)
        assert media_type.examples["user1"].value == "John"

    def test_media_type_with_encoding(self):
        """Test creating spec.mediatype.MediaType with encoding objects."""
        data = {
            "schema": {"type": "object"},
            "encoding": {
                "profileImage": {
                    "contentType": "image/png, image/jpeg",
                    "headers": {"X-Rate-Limit-Limit": {"schema": {"type": "integer"}}},
                },
            },
        }
        media_type = MediaType.from_dict(data)
        assert "profileImage" in media_type.encoding
        assert isinstance(media_type.encoding["profileImage"], spec.encoding.Encoding)
        assert media_type.encoding["profileImage"].contentType == "image/png, image/jpeg"


class TestEncoding:
    """Tests for spec.encoding.Encoding model."""

    def test_encoding_from_dict(self):
        """Test creating spec.encoding.Encoding from dict."""
        data = {
            "contentType": "application/xml; charset=utf-8",
            "style": "form",
            "explode": True,
            "allowReserved": False,
        }
        encoding = Encoding.from_dict(data)
        assert encoding.contentType == "application/xml; charset=utf-8"
        assert encoding.style == "form"
        assert encoding.explode is True
        assert encoding.allowReserved is False

    def test_encoding_with_headers(self):
        """Test creating spec.encoding.Encoding with headers."""
        data = {
            "contentType": "application/json",
            "headers": {
                "X-Custom-spec.header.Header": {"description": "Custom header", "schema": {"type": "string"}},
            },
        }
        encoding = Encoding.from_dict(data)
        assert "X-Custom-spec.header.Header" in encoding.headers


class TestLink:
    """Tests for spec.link.Link model."""

    def test_link_from_dict(self):
        """Test creating spec.link.Link from dict."""
        data = {
            "operationId": "getUser",
            "parameters": {"userId": "$response.body#/id"},
            "description": "spec.link.Link to user",
        }
        link = Link.from_dict(data)
        assert link.operationId == "getUser"
        assert link.description == "spec.link.Link to user"
        assert "userId" in link.parameters


class TestOAuthFlow:
    """Tests for spec.oauthflow.OAuthFlow model."""

    def test_oauth_flow_from_dict(self):
        """Test creating spec.oauthflow.OAuthFlow from dict."""
        data = {
            "authorizationUrl": "https://example.com/oauth/authorize",
            "tokenUrl": "https://example.com/oauth/token",
            "scopes": {
                "read": "Read access",
                "write": "Write access",
            },
        }
        flow = OAuthFlow.from_dict(data)
        assert flow.authorizationUrl == "https://example.com/oauth/authorize"
        assert flow.tokenUrl == "https://example.com/oauth/token"
        assert flow.scopes == {"read": "Read access", "write": "Write access"}


class TestOAuthFlows:
    """Tests for spec.oauthflows.OAuthFlows model."""

    def test_oauth_flows_from_dict(self):
        """Test creating spec.oauthflows.OAuthFlows from dict."""
        data = {
            "implicit": {
                "authorizationUrl": "https://example.com/oauth/authorize",
                "scopes": {"read": "Read access"},
            },
            "authorizationCode": {
                "authorizationUrl": "https://example.com/oauth/authorize",
                "tokenUrl": "https://example.com/oauth/token",
                "scopes": {"write": "Write access"},
            },
        }
        flows = OAuthFlows.from_dict(data)
        assert flows.implicit is not None
        assert flows.implicit.authorizationUrl == "https://example.com/oauth/authorize"
        assert flows.authorizationCode is not None
        assert flows.authorizationCode.tokenUrl == "https://example.com/oauth/token"
