# runtime/archive/archive_manager.py

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from shutil import copy2


class ArchiveManager:

    def __init__(self, archive_root="runtime/archive"):

        self.root = Path(archive_root)
        self.raw_dir = self.root / "raw"
        self.snapshots_dir = self.root / "snapshots"
        self.manifest_dir = self.root / "manifests"
        self.provenance_dir = self.root / "provenance"
        self.fingerprint_dir = self.root / "fingerprints"

        for d in [
            self.raw_dir,
            self.snapshots_dir,
            self.manifest_dir,
            self.provenance_dir,
            self.fingerprint_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)

    def store_file(self, filepath, source_url=None):

        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"{filepath} does not exist")

        sha256 = self._compute_sha256(filepath)

        archive_id = f"{filepath.stem}_{sha256[:8]}"

        dest_path = self.raw_dir / f"{archive_id}{filepath.suffix}"

        copy2(filepath, dest_path)

        manifest = {
            "archive_id": archive_id,
            "original_name": filepath.name,
            "stored_name": str(dest_path),
            "source_url": source_url,
            "sha256": sha256,
            "created_at": datetime.utcnow().isoformat(),
            "version": 1,
            "chunks": [],
            "embedding_ids": [],
            "graph_nodes": [],
            "agent_annotations": [],
        }

        manifest_path = self.manifest_dir / f"{archive_id}.json"

        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        if source_url:

            prov_path = self.provenance_dir / f"{archive_id}.json"

            with open(prov_path, "w") as f:
                json.dump(
                    {
                        "archive_id": archive_id,
                        "source_url": source_url,
                        "ingested_at": datetime.utcnow().isoformat(),
                    },
                    f,
                )

        fp_path = self.fingerprint_dir / f"{archive_id}.sha256"

        with open(fp_path, "w") as f:
            f.write(sha256)

        return archive_id

    def load_manifest(self, archive_id):

        manifest_path = self.manifest_dir / f"{archive_id}.json"

        if not manifest_path.exists():
            return None

        with open(manifest_path, "r") as f:
            return json.load(f)

    def update_manifest(self, archive_id, **kwargs):

        manifest = self.load_manifest(archive_id)

        if manifest is None:
            raise ValueError(f"No manifest for {archive_id}")

        manifest.update(kwargs)
        manifest["version"] += 1

        manifest_path = self.manifest_dir / f"{archive_id}.json"

        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

    def list_archives(self):

        manifests = []

        for f in self.manifest_dir.glob("*.json"):

            with open(f, "r") as fh:
                manifests.append(json.load(fh))

        return manifests

    def get_provenance(self, archive_id):

        prov_path = self.provenance_dir / f"{archive_id}.json"

        if not prov_path.exists():
            return None

        with open(prov_path, "r") as f:
            return json.load(f)

    def get_fingerprint(self, archive_id):

        fp_path = self.fingerprint_dir / f"{archive_id}.sha256"

        if not fp_path.exists():
            return None

        with open(fp_path, "r") as f:
            return f.read().strip()

    def _compute_sha256(self, filepath):

        sha256 = hashlib.sha256()

        with open(filepath, "rb") as f:

            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)

        return sha256.hexdigest()
