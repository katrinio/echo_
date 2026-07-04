# Releases

Releases are published automatically on push to `main` via [semantic-release](https://semantic-release.gitbook.io/).  
Versions are determined from commit messages using the [Conventional Commits](https://www.conventionalcommits.org/) format.  
Tags use the format `v1.0.0`; draft releases appear as `echo_ > v1.0.0`.

---

## Conventional Commits

Echo uses a trimmed-down set of commit types.

| Type       | Version | Purpose                                          | Example                                 |
|------------|---------|--------------------------------------------------|-----------------------------------------|
| `feat`     | Minor   | New user-facing feature                          | `feat(tags): add tag pages`             |
| `fix`      | Patch   | Bug fix                                          | `fix(terminal): preserve input on blur` |
| `feat!`    | Major   | Breaking change                                  | `feat!: redesign command parser`        |
| `fix!`     | Major   | Breaking fix                                     | `fix!: remove legacy slug format`       |
| `refactor` | —       | Internal change with no behavior impact          | `refactor(orm): extract base query`     |
| `docs`     | —       | Documentation, README, release notes             | `docs(readme): update setup guide`      |
| `test`     | —       | Tests                                            | `test(tags): add tag page tests`        |
| `ci`       | —       | CI/CD, Actions, Poetry, pre-commit, dependencies | `ci(release): add semantic release`     |

---

## Scope

Include a scope where it makes sense:

```
feat(tags): add tag autocomplete
fix(terminal): fix mobile input focus
refactor(orm): split milestone and tag models
docs(architecture): update structure section
ci(release): pin semantic-release version
```

---

## Rules

- Only `feat` and `fix` bump the version.
- `!` marks a breaking change → bumps major.
- All other types build a readable history but don't trigger a release.
- If a PR has multiple commits, the version is determined by the most significant one.
