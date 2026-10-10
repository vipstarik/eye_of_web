"""Utilities for a small, user-owned face gallery.

The gallery stores normalized face embeddings, not uploaded source images.  It is
intentionally independent from crawler, whitelist, EGM, and other global indexes.
"""

from __future__ import annotations

import numpy as np

EMBEDDING_DIM = 512
MIN_DETECTION_SCORE = 0.65


def normalize_embedding(embedding) -> np.ndarray:
    """Return a finite, L2-normalized 512-dimensional float32 embedding."""
    try:
        vector = np.asarray(embedding, dtype=np.float32).reshape(-1)
    except (TypeError, ValueError) as exc:
        raise ValueError("Yüz modeli geçerli bir vektör üretmedi.") from exc

    if vector.size != EMBEDDING_DIM:
        raise ValueError(
            f"Yüz vektörünün boyutu {EMBEDDING_DIM} olmalı (alınan: {vector.size})."
        )
    if not np.isfinite(vector).all():
        raise ValueError("Yüz vektörü geçersiz sayısal değerler içeriyor.")

    norm = float(np.linalg.norm(vector))
    if norm <= 1e-12:
        raise ValueError("Yüz vektörü boş veya sıfır uzunlukta.")

    return np.ascontiguousarray(vector / norm, dtype=np.float32)


def extract_single_face_embedding(image_bgr, face_analyzer):
    """Detect exactly one usable face and return ``(embedding, detection_score)``.

    InsightFace's ``FaceAnalysis.get`` expects an OpenCV/BGR image.  The caller is
    responsible for converting validated uploads to that format.
    """
    if face_analyzer is None:
        raise RuntimeError("Yüz analiz modeli başlatılmamış.")
    if image_bgr is None or not hasattr(image_bgr, "size") or image_bgr.size == 0:
        raise ValueError("Geçerli bir görsel gerekli.")

    detected_faces = face_analyzer.get(image_bgr)
    if not detected_faces:
        raise ValueError("Görselde yüz tespit edilemedi. Daha net bir fotoğraf deneyin.")
    if len(detected_faces) != 1:
        raise ValueError("Görselde tam olarak bir yüz olmalı.")

    face = detected_faces[0]
    try:
        detection_score = float(face.det_score)
    except (AttributeError, TypeError, ValueError):
        detection_score = 0.0

    if not np.isfinite(detection_score) or detection_score < MIN_DETECTION_SCORE:
        raise ValueError(
            "Yüz yeterince net algılanamadı. Yüzün görünür olduğu daha net bir fotoğraf deneyin."
        )

    embedding = normalize_embedding(getattr(face, "embedding", None))
    return embedding, detection_score


def rank_gallery_profiles(query_embedding, profiles, threshold=0.60, limit=10):
    """Rank profiles by their best cosine similarity to any enrolled sample.

    ``profiles`` is an iterable of dictionaries with ``id``, ``label``, and an
    ``embeddings`` iterable. Invalid stored vectors are skipped rather than
    breaking the whole search.
    """
    query = normalize_embedding(query_embedding)
    threshold = float(threshold)
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("Benzerlik eşiği 0 ile 1 arasında olmalı.")

    matches = []
    for profile in profiles:
        best_similarity = None
        for sample in profile.get("embeddings", ()):
            try:
                candidate = normalize_embedding(sample)
            except (TypeError, ValueError):
                continue
            similarity = float(np.clip(np.dot(query, candidate), -1.0, 1.0))
            if best_similarity is None or similarity > best_similarity:
                best_similarity = similarity

        if best_similarity is None or best_similarity < threshold:
            continue

        matches.append(
            {
                "id": profile["id"],
                "label": profile["label"],
                "sample_count": int(profile.get("sample_count", 0)),
                "similarity": best_similarity,
            }
        )

    matches.sort(key=lambda item: item["similarity"], reverse=True)
    return matches[: max(0, int(limit))]
