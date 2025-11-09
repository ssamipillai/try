import os
import re
import time
import math
from datetime import datetime
from pathlib import Path

DEFAULT_BASE = os.environ.get('MANAGER_NOTES_PATH') or str(Path.home() / 'notes' / 'manager')


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", '-', text)
    text = re.sub(r'-{2,}', '-', text)
    return text.strip('-')


class NotesManager:
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or DEFAULT_BASE).expanduser()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def create_note(self, title: str, tags: list[str] | None = None, open_in_editor: bool = True):
        tags = tags or []
        date_prefix = datetime.now().strftime('%Y-%m-%d')
        slug = _slugify(title if title else 'note')
        filename = f"{date_prefix}-{slug}.md"
        path = self.base_path / filename
        # If exists, append a suffix
        idx = 1
        while path.exists():
            path = self.base_path / f"{date_prefix}-{slug}-{idx}.md"
            idx += 1

        header = f"# {title}\n\n"
        if tags:
            header += f"**tags:** {', '.join(tags)}\n\n"
        header += f"_created: {datetime.now().isoformat()}_\n\n"

        path.write_text(header)

        if open_in_editor:
            self.open_in_editor(path)

        return path

    def list_notes(self):
        notes = []
        for p in self.base_path.iterdir():
            if p.is_file() and p.suffix.lower() in ('.md', '.txt'):
                stat = p.stat()
                notes.append({
                    'name': p.name,
                    'path': p,
                    'ctime': stat.st_ctime,
                    'mtime': stat.st_mtime,
                })
        return notes

    def read_note(self, filename: str) -> str:
        p = self.base_path / filename
        return p.read_text()

    def open_in_editor(self, path: Path):
        editor = os.environ.get('EDITOR')
        if editor:
            os.system(f'"{editor}" "{path}"')
            return

        # Fallbacks for Windows and others
        if os.name == 'nt':
            os.system(f'start "" "{path}"')
        else:
            # Try nano, vi, or pager
            for cmd in ('nano', 'vi'):
                if self._command_exists(cmd):
                    os.system(f'{cmd} "{path}"')
                    return
            # Last resort: print path
            print(f"Note created: {path}")

    def _command_exists(self, cmd: str) -> bool:
        from shutil import which
        return which(cmd) is not None

    # Fuzzy scoring inspired by try.rb
    def score_name(self, name: str, query: str, ctime: float | None = None, mtime: float | None = None) -> float:
        score = 0.0
        if name.startswith(datetime.now().strftime('%Y-')):
            score += 2.0

        if query:
            text_lower = name.lower()
            query_lower = query.lower()
            qchars = list(query_lower)
            last_pos = -1
            qi = 0
            for pos, ch in enumerate(text_lower):
                if qi >= len(qchars):
                    break
                if ch == qchars[qi]:
                    score += 1.0
                    if pos == 0 or not text_lower[pos-1].isalnum():
                        score += 1.0
                    if last_pos >= 0:
                        gap = pos - last_pos - 1
                        score += 1.0 / math.sqrt(gap + 1)
                    last_pos = pos
                    qi += 1

            if qi < len(qchars):
                return 0.0

            if last_pos >= 0:
                score *= (len(qchars) / (last_pos + 1))

            score *= (10.0 / (len(name) + 10.0))

        now = time.time()
        if ctime:
            days_old = (now - ctime) / 86400.0
            score += 2.0 / math.sqrt(days_old + 1)
        if mtime:
            hours = (now - mtime) / 3600.0
            score += 3.0 / math.sqrt(hours + 1)

        return score

    def search(self, query: str) -> list[dict]:
        notes = self.list_notes()
        scored = []
        for n in notes:
            s = self.score_name(n['name'], query, n['ctime'], n['mtime'])
            if query == '' or s > 0:
                n2 = n.copy()
                n2['score'] = s
                scored.append(n2)

        scored.sort(key=lambda x: -x['score'])
        return scored
