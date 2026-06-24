# echo_

STATUS: RUNNING

<p align="center">
  <img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWtuYnBucTE1dmFiOW15MTJ6MjR5ZjA5ZzI1MWcxY2tqZm5jMHIydSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l2JJvlHT0ERLhhhfO/giphy.gif" width="200"/>
</p>

-----
A small personal log of things worth remembering.
- Not a diary.
- Not a task tracker.
- Not a second brain.
- Just milestones.
---
Examples
```
2026-06-22
└─ VPN_FOR_FRIENDS

2026-06-21
└─ DOMAIN_AND_SSL

2026-05-27
└─ FINPIPE_V1_0_0
```

Each milestone has a title, a date, a description, tags and a stable slug.

```
title: VPN for friends
date: 2026-06-22
description: Психанула и подняла маленький VPN для друзей.
tags: [VPN, INFRA, FRIENDS]
slug: VPN_FOR_FRIENDS
```

Tags are freeform. Each tag links to a page listing all milestones that share it.

---
## Why

Most projects collect tasks.

This one collects moments.

A release.
A move.
A decision.
A strange idea at 2 a.m.
Something that would make it into a New Year's recap.

---
## Tech

- FastAPI
- Jinja2
- SQLite
- Alembic

- No frontend build step.
- No SPA.
- No JavaScript framework.

---
## Setup

```bash
poetry install
poetry run alembic upgrade head
poetry run uvicorn src.app:app --reload
```

If tables were already created before running migrations:

```bash
poetry run alembic stamp 4f1b2d9c7a11
```
