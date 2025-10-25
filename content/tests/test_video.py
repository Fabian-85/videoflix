import pytest
from django.urls import reverse
from content.models import Video
from pathlib import Path

def test_video_created(create_test_videos, settings):
    v1, v2 = create_test_videos
    for v in (v1, v2):
        for fld in ("hls_480p", "hls_720p"):
            rel = getattr(v, fld).name
            assert rel, f"{fld} fehlt"
            assert (Path(settings.MEDIA_ROOT) / rel).exists()

@pytest.mark.django_db
def test_video_list_api(api_client, create_test_videos, active_user):
    api_client.force_authenticate(user=active_user)
    url = reverse("video-list")
    response = api_client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    expected_keys = {"id", "created_at", "title", "description", "thumbnail_url", "category"}
    assert expected_keys.issubset(set(response.data[0].keys()))

@pytest.mark.django_db
def test_video_list_api_unauthenticated(api_client, create_test_videos):
    url = reverse("video-list")
    response = api_client.get(url)
    assert response.status_code == 401

@pytest.mark.django_db
def test_hsl_playlist_api(api_client, create_test_videos, active_user):
    api_client.force_authenticate(user=active_user)
    v1, _ = create_test_videos
    url = reverse("hsl-playlist", args=[v1.pk, "720p"])
    response = api_client.get(url)
    assert response.status_code == 200
    assert "#EXTM3U" in response.text
    assert response["Content-Type"] == "application/vnd.apple.mpegurl"

@pytest.mark.django_db
def test_hsl_playlist_api_unsupported_resolution(api_client, create_test_videos, active_user):
    api_client.force_authenticate(user=active_user)
    v1, _ = create_test_videos
    url = reverse("hsl-playlist", args=[v1.pk, "930p"])
    response = api_client.get(url)
    assert response.status_code == 404

@pytest.mark.django_db
def test_hsl_playlist_api_unauthenticated(api_client, create_test_videos, active_user):
    v1, _ = create_test_videos
    url = reverse("hsl-playlist", args=[v1.pk, "720p"])
    response = api_client.get(url)
    assert response.status_code == 401

@pytest.mark.django_db
def test_hsl_segment_api(api_client, create_test_videos, active_user):
    api_client.force_authenticate(user=active_user)
    v1, _ = create_test_videos
    url = reverse("hsl-segment", args=[v1.pk, "720p", "seg_000.ts"])
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "video/MP2T"
    
@pytest.mark.django_db
def test_hsl_segment_api_unauthenticated(api_client, create_test_videos, active_user):
    v1, _ = create_test_videos
    url = reverse("hsl-segment", args=[v1.pk, "720p", "seg_000.ts"])
    response = api_client.get(url)
    assert response.status_code == 401

@pytest.mark.django_db
def test_hsl_segment_api_unsupported_resolution(api_client, create_test_videos, active_user):
    api_client.force_authenticate(user=active_user)
    v1, _ = create_test_videos
    url = reverse("hsl-segment", args=[v1.pk, "920p", "seg_000.ts"])
    response = api_client.get(url)
    assert response.status_code == 404

@pytest.mark.django_db
def test_hsl_segment_api_segment_not_found(api_client, create_test_videos, active_user):
    api_client.force_authenticate(user=active_user)
    v1, _ = create_test_videos
    url = reverse("hsl-segment", args=[v1.pk, "720p", "missing.ts"])
    response = api_client.get(url)
    assert response.status_code == 404
    