import pytest
from django.urls import reverse
from pathlib import Path


def test_video_created(get_video, settings):
    video = get_video
    for fld in ("hls_480p", "hls_720p"):
            rel = getattr(video, fld).name
            assert rel, f"{fld} fehlt"
            assert (Path(settings.MEDIA_ROOT) / rel).exists()


@pytest.mark.django_db
def test_video_list_api(api_client, get_video, active_user):
    api_client.force_authenticate(user=active_user)
    url = reverse("video-list")
    response = api_client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    expected_keys = {"id", "created_at", "title", "description", "thumbnail_url", "category"}
    assert expected_keys.issubset(set(response.data[0].keys()))


@pytest.mark.django_db
def test_video_list_api_unauthenticated(api_client, get_video):
    url = reverse("video-list")
    response = api_client.get(url)
    assert response.status_code == 401
    

@pytest.mark.django_db
def test_hsl_playlist_api(api_client, get_video, active_user):
    api_client.force_authenticate(user=active_user)
    video = get_video
    url = reverse("hsl-playlist", args=[video.pk, "720p"])
    response = api_client.get(url)
    assert response.status_code == 200
    assert "#EXTM3U" in response.text
    assert response["Content-Type"] == "application/vnd.apple.mpegurl"


@pytest.mark.django_db
def test_hsl_playlist_api_unsupported_resolution(api_client, get_video, active_user):
    api_client.force_authenticate(user=active_user)
    video = get_video
    url = reverse("hsl-playlist", args=[video.pk, "930p"])
    response = api_client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_hsl_playlist_api_video_not_found(api_client, active_user):
    api_client.force_authenticate(user=active_user)
    url = reverse("hsl-playlist", args=[9999, "930p"])
    response = api_client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_hsl_playlist_api_unauthenticated(api_client, get_video, active_user):
    video = get_video
    url = reverse("hsl-playlist", args=[video.pk, "720p"])
    response = api_client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_hsl_segment_api(api_client, get_video, active_user):
    api_client.force_authenticate(user=active_user)
    video = get_video
    url = reverse("hsl-segment", args=[video.pk, "720p", "seg_000.ts"])
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "video/MP2T"


@pytest.mark.django_db
def test_hsl_segment_api_unauthenticated(api_client, get_video, active_user):
    video = get_video
    url = reverse("hsl-segment", args=[video.pk, "720p", "seg_000.ts"])
    response = api_client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_hsl_segment_api_unsupported_resolution(api_client, get_video, active_user):
    api_client.force_authenticate(user=active_user)
    video = get_video
    url = reverse("hsl-segment", args=[video.pk, "920p", "seg_000.ts"])
    response = api_client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_hsl_segment_api_video_not_found(api_client, active_user):
    api_client.force_authenticate(user=active_user)
    url = reverse("hsl-segment", args=[9999, "920p", "seg_000.ts"])
    response = api_client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_hsl_segment_api_segment_not_found(api_client, get_video, active_user):
    api_client.force_authenticate(user=active_user)
    video = get_video
    url = reverse("hsl-segment", args=[video.pk, "720p", "missing.ts"])
    response = api_client.get(url)
    assert response.status_code == 404
    