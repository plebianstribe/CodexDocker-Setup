from fastapi.testclient import TestClient

from seemycitations.main import app


def test_home_exposes_accessible_workflow_landmarks() -> None:
    html = TestClient(app).get("/").text
    assert '<main>' in html
    assert 'aria-live="polite"' in html
    assert 'id="author-search"' in html
    assert 'id="document-select"' in html
    assert 'id="analysis-form"' in html
    assert 'No API key is required.' in html
