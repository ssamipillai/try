# manager_notes

Lightweight daily notes CLI for senior managers. Creates dated Markdown notes, supports tagging and fuzzy search.

Quick start:

```powershell
# Initialize (optional)
python -m manager_notes.cli init C:\Users\you\notes\manager

# Create a new note
python -m manager_notes.cli new "Weekly sync - product" -t product,team

# List notes
python -m manager_notes.cli list sync

# Show note content
python -m manager_notes.cli show 2025-11-09-weekly-sync-product.md
```

Defaults to `~/notes/manager` if `MANAGER_NOTES_PATH` isn't set.
