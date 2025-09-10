# Claude Code Notifier Project

## What This Project Is

A macOS notification system for Claude Code that provides intelligent click-to-focus functionality when Claude Code completes tasks or encounters errors.

## What We're Trying to Accomplish

**Primary Goals:**
- Provide instant notification when Claude Code completes operations
- Enable one-click return to the originating application (IDE, terminal, etc.)
- Smart notification logic that only notifies when user attention has moved elsewhere
- Fast, reliable execution as a Claude Code hook
- Cross-application support

**Technical Objectives:**
- Python-based implementation leveraging modern libraries (psutil, PyObjC)
- Window detection and focus management on macOS
- JSON-based communication with Claude Code hooks
- Performance optimization for sub-100ms execution
- No background daemons - hook-triggered execution only

## Why We're Doing This

**The Problem:**
- Long-running Claude Code tasks can complete while user attention is elsewhere
- No built-in mechanism to return focus to the original development context
- Manual window switching disrupts development flow
- Miss important completions or error notifications

**The Solution Benefits:**
- **Instant Awareness**: Immediate notification of task completion
- **Seamless Return**: One-click focus return to your IDE or terminal
- **Smart Logic**: Only notifies when actually needed (focus has changed)
- **Universal Support**: Works with VS Code, Cursor, IntelliJ, iTerm, Terminal, etc.
- **Non-Intrusive**: No background processes, minimal system impact

## Files and Structure

```
claude-code-notifier/
├── src/                          # Python source code
│   ├── __init__.py              # Package initialization
│   ├── window_test.py           # Proof-of-concept validation script
│   └── [future notification modules]
├── tests/                       # Test suite (future)
├── pyproject.toml              # Python project configuration
├── Makefile                    # Development commands
├── .pre-commit-config.yaml     # Code quality hooks
├── .gitignore                  # Version control exclusions
└── CLAUDE.md                   # Project documentation
```

## Development Environment

**CRITICAL**: Always activate virtual environment before running Python commands:
```bash
source .venv/bin/activate
```

## Development Commands

```bash
# Quality checks
make check          # Full quality gate (format, lint, typecheck, test)
make format         # Format code with ruff
make lint           # Lint with ruff  
make typecheck      # Type check with mypy
make test           # Run test suite
make fix            # Auto-fix all fixable issues

# Development workflow
make install        # Install development dependencies
make clean          # Clean temporary files
make help           # Show all commands
```

## Key Development Notes

- **Virtual Environment**: Required for all Python operations to avoid system conflicts
- **Quality Gates**: All code must pass format, lint, typecheck, and test before commits
- **Performance Focus**: Target <100ms execution time for notification hooks
- **macOS Integration**: Leverages native macOS APIs through PyObjC frameworks
- **No Daemons**: Hook-triggered execution only, no background processes

## Success Metrics

**Performance:**
- Notification execution <100ms
- Window detection <50ms
- JSON parsing <1ms

**Functionality:**
- Accurate originating application detection
- Reliable focus state detection
- Correct bundle ID mapping for all supported applications
- Seamless Claude Code hook integration

**Reliability:**
- Zero false notifications
- 100% hook compatibility
- Graceful error handling and fallbacks

---

*This project provides the missing link between Claude Code's powerful automation and seamless development workflow integration.*