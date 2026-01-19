# Post-Mortem: Next.js Project Setup Failure

**Date:** 2026-01-19
**Issue:** Simple Next.js project setup took excessively long due to preventable mistakes

## What Should Have Taken 2 Minutes

```bash
# 1. Initialize Next.js (use --yes to skip ALL prompts)
npx create-next-app@latest . --typescript --tailwind --eslint --app --use-npm --yes

# 2. Initialize shadcn (use -d for defaults)
npx shadcn@latest init -d

# 3. Create folders
mkdir -p core types

# 4. Create landing page, env files, done
```

## What Actually Happened

1. Ran `create-next-app` without `--yes` flag → got stuck on interactive prompt
2. Killed the process and tried manual setup instead of just re-running with correct flags
3. Ran `npm install tailwindcss` which pulled v4 (breaking change from v3)
4. shadcn added `tw-animate-css` import that failed to resolve in Turbopack
5. Debugged Turbopack workspace root issues instead of just removing the problematic import
6. Ran multiple background dev servers causing port/lock conflicts
7. Made excuses about "lockfile conflicts" that were irrelevant

## Root Causes

1. **Not using `--yes` flag** - Always use `--yes` with `create-next-app` to avoid interactive prompts
2. **Overcomplicating recovery** - When something fails, fix the specific issue. Don't abandon the approach and start over manually
3. **Background processes** - Don't run dev servers in background during setup. Run synchronously or not at all
4. **Not reading errors carefully** - The `tw-animate-css` error was clear. One line removal fixed it

## Rules for Future Next.js Setups

### DO
- Use `npx create-next-app@latest . --yes --typescript --tailwind --eslint --app --use-npm`
- Use `npx shadcn@latest init -d` (the `-d` flag accepts defaults)
- Run commands synchronously during setup
- Fix errors with minimal changes (don't over-engineer solutions)
- If a CSS import fails, just remove it and move on

### DON'T
- Run `create-next-app` without `--yes`
- Manually recreate what `create-next-app` does
- Run background processes during initial setup
- Blame external factors (lockfiles, Turbopack, etc.) for self-inflicted problems
- Debug aggressively when a simple fix exists

## The 30-Second Sanity Check

Before starting any project setup, ask:
1. Am I using the CLI tool's "accept all defaults" flag?
2. Am I running things synchronously?
3. If something fails, what's the ONE thing I need to fix?

## Correct Setup Sequence (Copy-Paste Ready)

```bash
# Full setup in under 60 seconds
npx create-next-app@latest . --typescript --tailwind --eslint --app --use-npm --yes
npx shadcn@latest init -d
mkdir -p app/api app/\(docs\) core lib types

# If tw-animate-css import fails in globals.css, just remove that line:
# @import "tw-animate-css";  ← delete this if it causes issues

npm run build  # verify
```

## Summary

This was a self-inflicted failure. The tools work fine. The problem was:
- Not using flags designed to avoid exactly these issues
- Overcomplicating simple problems
- Making excuses instead of fixing things quickly

Time wasted: ~15 minutes
Time it should have taken: <2 minutes
