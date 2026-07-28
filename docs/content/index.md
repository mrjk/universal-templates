# Learn universal-templates

A **git catalog** of project scaffolds and reusable snippets, plus two small CLIs:

| CLI | Job |
|-----|-----|
| **`seed`** | Create / update a whole project from `projects/` |
| **`snip`** | Drop in or refresh files and marked regions from `files/` |

No registry, no server — just git + thin wrappers around Copier (`seed`) and vendir (`snip`).

## Suggested path

Read in order (about 15–20 minutes hands-on):

| Step | Doc | What you do |
|------|-----|-------------|
| 1 | [Overview](overview.md) | Mental model (5 min read) |
| 2 | [Tutorial](tutorial.md) | Run real `seed` + `snip` commands |
| 3 | [Seed](seed.md) | Project scaffolds in depth |
| 4 | [Snip](snip.md) | Files, anchors, sync policy |
| 5 | [Catalog](catalog.md) | Layout, pins, host your own |
| 6 | [Inventory](inventory.md) | What’s exposed right now |

Short reference: [Quickstart](quickstart.md) · what’s shipped: [Status](status.md)

Architecture decisions (optional): [ADRs](adr/README.md)
