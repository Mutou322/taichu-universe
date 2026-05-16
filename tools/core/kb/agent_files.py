"""Per‑agent file management: profile, personality, and session logs.

Each registered agent gets a directory under knowledge/agents/{agent_id}/:
  profile.yaml      — system‑maintained metadata (last_seen, type, …)
  personality.md    — editable personality / instructions file
  sessions/         — daily session logs (YYYY‑MM‑DD.md)
"""

from datetime import date, datetime, timezone
from pathlib import Path

import yaml

from config.paths import paths

_MGR: "AgentFileManager | None" = None


def get_manager() -> "AgentFileManager":
    global _MGR
    if _MGR is None:
        _MGR = AgentFileManager()
    return _MGR


class AgentFileManager:
    """Manages per‑agent files under knowledge/agents/{agent_id}/."""

    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir or paths.knowledge.agents).expanduser()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    # ── helpers ──

    def _agent_path(self, agent_id: str) -> Path:
        return self.base_dir / agent_id

    def _profile_path(self, agent_id: str) -> Path:
        return self._agent_path(agent_id) / "profile.yaml"

    def _personality_path(self, agent_id: str) -> Path:
        return self._agent_path(agent_id) / "personality.md"

    def _sessions_dir(self, agent_id: str) -> Path:
        return self._agent_path(agent_id) / "sessions"

    # ── directory lifecycle ──

    def ensure_agent_dir(self, agent_id: str, agent_type: str = "external", meta: dict | None = None) -> bool:
        """Create agent directory + default files if missing. Returns True if newly created."""
        agent_dir = self._agent_path(agent_id)
        if agent_dir.exists():
            return False

        agent_dir.mkdir(parents=True, exist_ok=True)
        self._sessions_dir(agent_id).mkdir(parents=True, exist_ok=True)

        # default profile.yaml
        if not self._profile_path(agent_id).exists():
            profile = {
                "agent_id": agent_id,
                "type": agent_type,
                "meta": meta or {},
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_seen": datetime.now(timezone.utc).isoformat(),
            }
            with open(self._profile_path(agent_id), "w", encoding="utf-8") as f:
                yaml.dump(profile, f, allow_unicode=True, default_flow_style=False)

        # default personality.md
        if not self._personality_path(agent_id).exists():
            self._personality_path(agent_id).write_text(
                f"# {agent_id}\n\nPersonality and instructions for this agent.\n",
                encoding="utf-8",
            )

        return True

    def remove_agent_dir(self, agent_id: str) -> bool:
        """Remove agent directory and all contents."""
        agent_dir = self._agent_path(agent_id)
        if not agent_dir.exists():
            return False
        import shutil

        shutil.rmtree(agent_dir)
        return True

    # ── profile ──

    def get_profile(self, agent_id: str) -> dict | None:
        path = self._profile_path(agent_id)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def update_profile(self, agent_id: str, updates: dict) -> dict | None:
        path = self._profile_path(agent_id)
        profile = self.get_profile(agent_id) or {}
        profile.update(updates)
        profile["last_seen"] = datetime.now(timezone.utc).isoformat()
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(profile, f, allow_unicode=True, default_flow_style=False)
        return profile

    # ── personality ──

    def get_personality(self, agent_id: str) -> str | None:
        path = self._personality_path(agent_id)
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def update_personality(self, agent_id: str, content: str) -> bool:
        self._personality_path(agent_id).write_text(content, encoding="utf-8")
        self.update_profile(agent_id, {})  # bump last_seen
        return True

    # ── session logs ──

    def append_session(self, agent_id: str, entry: dict) -> bool:
        """Append a log entry to today's session file."""
        sessions_dir = self._sessions_dir(agent_id)
        sessions_dir.mkdir(parents=True, exist_ok=True)

        today = date.today().isoformat()
        session_file = sessions_dir / f"{today}.md"

        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        line = f"- **{timestamp}** | {entry.get('type', 'message')}"
        if entry.get("content"):
            line += f": {entry['content']}"
        line += "\n"

        with open(session_file, "a", encoding="utf-8") as f:
            f.write(line)

        return True

    def list_sessions(self, agent_id: str) -> list[dict]:
        """List available session dates with entry counts."""
        sessions_dir = self._sessions_dir(agent_id)
        if not sessions_dir.exists():
            return []
        results = []
        for p in sorted(sessions_dir.glob("*.md"), reverse=True):
            lines = p.read_text(encoding="utf-8").strip().splitlines()
            results.append({"date": p.stem, "entries": len(lines), "path": str(p)})
        return results

    def get_session(self, agent_id: str, date_str: str) -> str | None:
        """Get full session log for a specific date (YYYY‑MM‑DD)."""
        session_file = self._sessions_dir(agent_id) / f"{date_str}.md"
        if not session_file.exists():
            return None
        return session_file.read_text(encoding="utf-8")

    def list_agents(self) -> list[str]:
        """List all agent IDs that have directories."""
        return sorted(d.name for d in self.base_dir.iterdir() if d.is_dir() and not d.name.startswith("."))


# ── top‑level callbacks for integration ──


def on_agent_registered(agent_id: str, agent_type: str = "external", meta: dict | None = None) -> dict | None:
    """Called when an agent registers — ensure dir and return profile."""
    mgr = get_manager()
    mgr.ensure_agent_dir(agent_id, agent_type, meta)
    return mgr.get_profile(agent_id)


def on_memory_stored(
    agent_id: str,
    memory_type: str = "conversation",
    content: str = "",
    session_id: str = "",
) -> bool:
    """Called after a memory is saved — append to today's session log."""
    mgr = get_manager()
    mgr.ensure_agent_dir(agent_id)
    return mgr.append_session(
        agent_id,
        {
            "type": memory_type,
            "content": content,
            "session_id": session_id,
        },
    )
