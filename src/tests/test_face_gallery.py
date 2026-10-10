import unittest
from types import SimpleNamespace

import numpy as np

from lib.face_gallery import (
    extract_single_face_embedding,
    normalize_embedding,
    rank_gallery_profiles,
)


class FakeAnalyzer:
    def __init__(self, faces):
        self.faces = faces

    def get(self, image):
        return self.faces


class FaceGalleryTests(unittest.TestCase):
    def setUp(self):
        self.image = np.zeros((16, 16, 3), dtype=np.uint8)
        self.embedding = np.zeros(512, dtype=np.float32)
        self.embedding[0] = 1.0

    def test_normalize_embedding_returns_unit_vector(self):
        vector = normalize_embedding(self.embedding * 3)
        self.assertEqual(vector.shape, (512,))
        self.assertAlmostEqual(float(np.linalg.norm(vector)), 1.0, places=6)

    def test_extracts_exactly_one_clear_face(self):
        face = SimpleNamespace(det_score=0.95, embedding=self.embedding)
        vector, score = extract_single_face_embedding(
            self.image, FakeAnalyzer([face])
        )
        np.testing.assert_allclose(vector, self.embedding)
        self.assertAlmostEqual(score, 0.95)

    def test_rejects_no_face_and_multiple_faces(self):
        with self.assertRaisesRegex(ValueError, "yüz tespit edilemedi"):
            extract_single_face_embedding(self.image, FakeAnalyzer([]))

        face = SimpleNamespace(det_score=0.95, embedding=self.embedding)
        with self.assertRaisesRegex(ValueError, "tam olarak bir yüz"):
            extract_single_face_embedding(self.image, FakeAnalyzer([face, face]))

    def test_rejects_low_confidence_and_invalid_embeddings(self):
        low_confidence_face = SimpleNamespace(det_score=0.2, embedding=self.embedding)
        with self.assertRaisesRegex(ValueError, "yeterince net"):
            extract_single_face_embedding(
                self.image, FakeAnalyzer([low_confidence_face])
            )

        with self.assertRaisesRegex(ValueError, "boyutu"):
            normalize_embedding(np.ones(128, dtype=np.float32))

    def test_ranks_only_profiles_over_threshold(self):
        unrelated = np.zeros(512, dtype=np.float32)
        unrelated[1] = 1.0
        profiles = [
            {
                "id": 1,
                "label": "A",
                "sample_count": 2,
                "embeddings": [unrelated, self.embedding],
            },
            {
                "id": 2,
                "label": "B",
                "sample_count": 1,
                "embeddings": [unrelated],
            },
        ]

        results = rank_gallery_profiles(
            self.embedding, profiles, threshold=0.60, limit=10
        )
        self.assertEqual([result["id"] for result in results], [1])
        self.assertAlmostEqual(results[0]["similarity"], 1.0, places=6)
        self.assertEqual(results[0]["sample_count"], 2)


if __name__ == "__main__":
    unittest.main()
