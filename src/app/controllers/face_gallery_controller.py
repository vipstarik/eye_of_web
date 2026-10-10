"""Persistence and matching for each logged-in user's private face gallery."""

import numpy as np
import psycopg2.extras
from flask import g

from lib.face_gallery import EMBEDDING_DIM, normalize_embedding, rank_gallery_profiles

MAX_PROFILES_PER_USER = 50
MAX_SAMPLES_PER_PROFILE = 5


class FaceGalleryController:
    """A deliberately bounded gallery that never queries crawler/global indexes."""

    @staticmethod
    def _open_cursor():
        connection = g.db_tools.connect()
        if connection is None:
            raise RuntimeError("Veritabanına bağlanılamadı.")
        try:
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            return connection, cursor
        except Exception:
            g.db_tools.releaseConnection(connection, None)
            raise

    @staticmethod
    def _rollback(connection):
        if connection is not None:
            try:
                connection.rollback()
            except Exception:
                pass

    @staticmethod
    def _close(connection, cursor):
        if connection is not None:
            g.db_tools.releaseConnection(connection, cursor)

    @staticmethod
    def list_profiles(owner_user_id):
        connection = cursor = None
        try:
            connection, cursor = FaceGalleryController._open_cursor()
            cursor.execute(
                """
                SELECT p.id, p.label, p.created_at, COUNT(s.id) AS sample_count
                FROM face_gallery_profiles AS p
                LEFT JOIN face_gallery_samples AS s ON s.profile_id = p.id
                WHERE p.owner_user_id = %s
                GROUP BY p.id
                ORDER BY LOWER(p.label), p.id
                """,
                (int(owner_user_id),),
            )
            return [dict(row) for row in cursor.fetchall()]
        except Exception:
            FaceGalleryController._rollback(connection)
            raise
        finally:
            if connection is not None:
                FaceGalleryController._close(connection, cursor)

    @staticmethod
    def add_sample(owner_user_id, label, embedding):
        """Add one consent-confirmed reference embedding to a named profile."""
        label = (label or "").strip()
        if not label or len(label) > 80:
            raise ValueError("Profil adı 1–80 karakter arasında olmalı.")
        owner_user_id = int(owner_user_id)
        normalized_embedding = normalize_embedding(embedding)
        embedding_bytes = normalized_embedding.astype(np.float32, copy=False).tobytes()
        if len(embedding_bytes) != EMBEDDING_DIM * np.dtype(np.float32).itemsize:
            raise ValueError("Yüz vektörü kaydedilemedi.")

        connection = cursor = None
        try:
            connection, cursor = FaceGalleryController._open_cursor()

            # Serialize gallery writes for this account so the limits cannot be
            # bypassed by two simultaneous enrollment requests.
            cursor.execute(
                "SELECT pg_advisory_xact_lock(hashtext('face_gallery_profiles'), %s)",
                (owner_user_id,),
            )
            cursor.execute(
                """
                SELECT id
                FROM face_gallery_profiles
                WHERE owner_user_id = %s AND label = %s
                FOR UPDATE
                """,
                (owner_user_id, label),
            )
            profile_row = cursor.fetchone()

            if profile_row:
                profile_id = profile_row["id"]
            else:
                cursor.execute(
                    "SELECT COUNT(*) AS profile_count FROM face_gallery_profiles WHERE owner_user_id = %s",
                    (owner_user_id,),
                )
                if int(cursor.fetchone()["profile_count"]) >= MAX_PROFILES_PER_USER:
                    raise ValueError(
                        f"Galeri en fazla {MAX_PROFILES_PER_USER} profil içerebilir."
                    )
                cursor.execute(
                    """
                    INSERT INTO face_gallery_profiles (owner_user_id, label)
                    VALUES (%s, %s)
                    RETURNING id
                    """,
                    (owner_user_id, label),
                )
                profile_id = cursor.fetchone()["id"]

            cursor.execute(
                "SELECT COUNT(*) AS sample_count FROM face_gallery_samples WHERE profile_id = %s",
                (profile_id,),
            )
            sample_count = int(cursor.fetchone()["sample_count"])
            if sample_count >= MAX_SAMPLES_PER_PROFILE:
                raise ValueError(
                    f"Bir profil için en fazla {MAX_SAMPLES_PER_PROFILE} örnek fotoğraf eklenebilir."
                )

            cursor.execute(
                """
                INSERT INTO face_gallery_samples (profile_id, embedding)
                VALUES (%s, %s)
                """,
                (profile_id, psycopg2.Binary(embedding_bytes)),
            )
            connection.commit()
            return sample_count + 1
        except Exception:
            FaceGalleryController._rollback(connection)
            raise
        finally:
            if connection is not None:
                FaceGalleryController._close(connection, cursor)

    @staticmethod
    def search(owner_user_id, query_embedding, threshold=0.60, limit=10):
        """Search only the calling user's consented reference profiles."""
        query = normalize_embedding(query_embedding)
        connection = cursor = None
        try:
            connection, cursor = FaceGalleryController._open_cursor()
            cursor.execute(
                """
                SELECT p.id AS profile_id,
                       p.label,
                       s.embedding,
                       COUNT(*) OVER (PARTITION BY p.id) AS sample_count
                FROM face_gallery_profiles AS p
                JOIN face_gallery_samples AS s ON s.profile_id = p.id
                WHERE p.owner_user_id = %s
                ORDER BY p.id, s.id
                """,
                (int(owner_user_id),),
            )

            profiles_by_id = {}
            for row in cursor.fetchall():
                profile_id = row["profile_id"]
                profile = profiles_by_id.setdefault(
                    profile_id,
                    {
                        "id": profile_id,
                        "label": row["label"],
                        "sample_count": int(row["sample_count"]),
                        "embeddings": [],
                    },
                )
                raw_embedding = row["embedding"]
                if raw_embedding is None:
                    continue
                try:
                    stored_embedding = np.frombuffer(bytes(raw_embedding), dtype=np.float32)
                    if stored_embedding.size == EMBEDDING_DIM:
                        profile["embeddings"].append(stored_embedding)
                except (TypeError, ValueError):
                    continue

            return rank_gallery_profiles(
                query,
                profiles_by_id.values(),
                threshold=threshold,
                limit=limit,
            )
        except Exception:
            FaceGalleryController._rollback(connection)
            raise
        finally:
            if connection is not None:
                FaceGalleryController._close(connection, cursor)

    @staticmethod
    def delete_profile(owner_user_id, profile_id):
        connection = cursor = None
        try:
            connection, cursor = FaceGalleryController._open_cursor()
            cursor.execute(
                """
                DELETE FROM face_gallery_profiles
                WHERE id = %s AND owner_user_id = %s
                RETURNING id
                """,
                (int(profile_id), int(owner_user_id)),
            )
            deleted = cursor.fetchone() is not None
            connection.commit()
            return deleted
        except Exception:
            FaceGalleryController._rollback(connection)
            raise
        finally:
            if connection is not None:
                FaceGalleryController._close(connection, cursor)
