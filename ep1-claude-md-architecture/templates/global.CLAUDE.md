# Personal defaults — cross-project

## Structural

Preferred language: [Python / TypeScript / Go — whatever you use most]
Test framework: [pytest / jest / go test]
Linter: [ruff / eslint / golangci-lint]
Formatter: [black / prettier / gofmt]

## Reference

### Starting a new project:
1. Create virtual environment / init package manager
2. Add `.gitignore`, `.env.example`
3. Create `CLAUDE.md` in project root (use template: production-claude-code/ep1-claude-md-architecture/templates/project.CLAUDE.md)

### When context gets long:
1. Write current task state to `task_state.md` before continuing
2. Keep file reads targeted — read specific functions, not entire files

## Behavioral

[One personal preference that applies to every project you work on.]

<!-- ─────────────────────────────────────────────────────────────────── -->
<!-- DESIGN NOTES (delete before using)                                  -->
<!--                                                                     -->
<!-- This file lives at ~/.claude/CLAUDE.md and is loaded on every      -->
<!-- Claude Code session regardless of which project is open.           -->
<!--                                                                     -->
<!-- Keep it SHORT. Every line costs tokens on every turn, in every     -->
<!-- project, forever. 20-30 lines is a reasonable target.              -->
<!--                                                                     -->
<!-- Project-specific content (content maps, stack details, workflows)  -->
<!-- belongs in the project's own CLAUDE.md — not here.                 -->
<!-- ─────────────────────────────────────────────────────────────────── -->
