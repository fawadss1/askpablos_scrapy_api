"""Tests for askpablos_scrapy_api package."""
import json
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from askpablos_scrapy_api.operations import AskPablosAPIMapValidator, create_api_payload
from askpablos_scrapy_api.exceptions import AskPablosAPIError, AuthenticationError, RateLimitError, handle_api_error
from askpablos_scrapy_api.auth import sign_request, create_auth_headers
from askpablos_scrapy_api.config import Config

validate = AskPablosAPIMapValidator.validate_config


# --- helpers ---
def op(on="css", rule="visible", value=".selector", **extra):
    return {"task": "waitForElement", "match": {"on": on, "rule": rule, "value": value}, **extra}


# --- browser ---
def test_browser_valid():
    assert validate({"browser": True})["browser"] is True
    assert validate({"browser": False})["browser"] is False
    assert "browser" not in validate({})


def test_browser_invalid():
    with pytest.raises(ValueError): validate({"browser": "yes"})
    with pytest.raises(ValueError): validate({"browser": 1})
    with pytest.raises(ValueError): validate("browser=True")


# --- screenshot ---
def test_screenshot_valid():
    assert validate({"browser": True, "screenshot": True})["screenshot"] is True
    assert validate({"screenshot": True})["screenshot"] is True  # warns, not raises


def test_screenshot_invalid():
    with pytest.raises(ValueError): validate({"screenshot": "yes"})


# --- geoLocation ---
@pytest.mark.parametrize("code", ["PK", "US", "pk", "us", " US "])
def test_geo_location_valid(code):
    assert validate({"geoLocation": code})["geoLocation"] == code.strip().lower()


@pytest.mark.parametrize("bad", ["USA", "P1", "", "  ", 123])
def test_geo_location_invalid(bad):
    with pytest.raises(ValueError): validate({"geoLocation": bad})


# --- proxyType ---
@pytest.mark.parametrize("pt", ["datacenter", "residential", "mobile"])
def test_proxy_type_valid(pt):
    assert validate({"proxyType": pt})["proxyType"] == pt


@pytest.mark.parametrize("bad", ["DATACENTER", "dsl", "", 123])
def test_proxy_type_invalid(bad):
    with pytest.raises(ValueError): validate({"proxyType": bad})


# --- operations ---
def test_operations_valid():
    ops = [op()]
    assert validate({"browser": True, "operations": ops})["operations"] == ops
    assert validate({"operations": ops})["operations"] == ops  # warns, not raises


def test_operations_xpath_valid():
    ops = [op(on="xpath", rule="attached", value="//div[@id='main']")]
    assert validate({"browser": True, "operations": ops})["operations"] == ops


@pytest.mark.parametrize("bad,match", [
    ({"browser": True, "operations": "click"}, "'operations' must be a list"),
    ({"browser": True, "operations": ["click"]}, None),
    ({"browser": True, "operations": [{"match": {"on": "css", "rule": "visible", "value": ".x"}}]}, "missing required field 'task'"),
    ({"browser": True, "operations": [{**op(), "task": "click"}]}, "'task' must be one of"),
    ({"browser": True, "operations": [{"task": "waitForElement"}]}, "missing required field 'match'"),
])
def test_operations_invalid(bad, match):
    kw = {"match": match} if match else {}
    with pytest.raises(ValueError, **kw): validate(bad)


@pytest.mark.parametrize("bad_op,match", [
    ({**op(), "match": "css:.x"}, "'match' must be a dictionary"),
    ({**op(), "match": {**op()["match"], "on": "jquery"}}, "'match.on' must be one of"),
    ({**op(), "match": {**op()["match"], "rule": "exists"}}, "'match.rule' must be one of"),
    ({"task": "waitForElement", "match": {"on": "css", "rule": "visible"}}, "missing required field 'value'"),
    ({**op(), "match": {**op()["match"], "value": 123}}, "'match.value' must be a string"),
    (op(on="xpath", value="#main"), "appears to be a CSS selector"),
    (op(on="css", value="//div"), "appears to be an XPath selector"),
    (op(on="css", value="div[@class]"), "contains XPath syntax"),
    ({**op(), "maxWait": "5s"}, "'maxWait' must be a number"),
    ({**op(), "maxWait": 0}, "'maxWait' must be greater than 0"),
    ({**op(), "onFailure": "ignore"}, "'onFailure' must be one of"),
])
def test_operations_field_invalid(bad_op, match):
    with pytest.raises(ValueError, match=match): validate({"browser": True, "operations": [bad_op]})


def test_operations_optional_fields_valid():
    o = {**op(), "maxWait": 5, "onFailure": "continue"}
    result = validate({"browser": True, "operations": [o]})
    assert result["operations"][0]["maxWait"] == 5
    assert result["operations"][0]["onFailure"] == "continue"


# --- create_api_payload ---
def test_payload_required_fields():
    cfg = validate({"browser": True})
    p = create_api_payload("https://example.com", "GET", cfg)
    assert p == {"url": "https://example.com", "method": "GET", "browser": True}


def test_payload_optional_fields():
    cfg = validate({"browser": True, "screenshot": True, "geoLocation": "us", "proxyType": "residential"})
    p = create_api_payload("https://example.com", "GET", cfg)
    assert p["geoLocation"] == "us" and p["proxyType"] == "residential" and p["screenshot"] is True


def test_payload_browser_defaults_false():
    assert create_api_payload("https://example.com", "GET", {})["browser"] is False


# --- exceptions ---
def test_api_error():
    assert "400" in str(AskPablosAPIError("bad", status_code=400))
    assert AskPablosAPIError("x", response={"error": "quota exceeded"}).message == "quota exceeded"


@pytest.mark.parametrize("code,cls",
                         [(401, AuthenticationError), (403, AuthenticationError), (429, RateLimitError), (500, AskPablosAPIError)])
def test_handle_api_error(code, cls):
    assert isinstance(handle_api_error(code), cls)


def test_rate_limit_parses_info():
    err = handle_api_error(429, {"error": "x", "rateLimit": {"resetAt": "2026-04-01", "limit": 100, "remaining": 0}})
    assert err.reset_time == "2026-04-01" and err.limit == 100


# --- auth ---
def test_sign_request():
    rj, sig = sign_request({"url": "https://x.com", "b": 1}, "secret")
    assert json.loads(rj)["url"] == "https://x.com"
    assert sign_request({"a": 1}, "k")[1] == sign_request({"a": 1}, "k")[1]  # deterministic
    assert sign_request({"a": 1}, "k1")[1] != sign_request({"a": 1}, "k2")[1]  # different keys


def test_sign_request_sorted_keys():
    rj, _ = sign_request({"z": 1, "a": 2}, "k")
    assert list(json.loads(rj).keys()) == ["a", "z"]


def test_create_auth_headers():
    h = create_auth_headers("key", "sig==")
    assert h == {"Content-Type": "application/json", "X-API-Key": "key", "X-Signature": "sig=="}


# --- config ---
def _cfg(**kw):
    c = Config()
    c.load_from_settings({"API_KEY": "k", "SECRET_KEY": "s", **kw})
    return c


def test_config_validate():
    _cfg().validate()
    with pytest.raises(ValueError, match="API_KEY"):    Config().validate()  # empty
    with pytest.raises(ValueError, match="SECRET_KEY"): (lambda c: (c.load_from_settings({"API_KEY": "k"}), c.validate()))(Config())


def test_config_values():
    assert _cfg().get("TIMEOUT") == Config.DEFAULT_TIMEOUT
    assert _cfg(TIMEOUT=60).get("TIMEOUT") == 60
    assert _cfg(APCLOUDY_URL="http://host").API_URL == "http://host/api/proxy/"
    assert _cfg().get("X", "fallback") == "fallback"
