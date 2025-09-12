# Minimal Notification System Plan

## Core Concept
Universal click-to-focus notifications using Hammerspoon's cross-space window detection breakthrough.

## The Breakthrough
✅ **Cross-Space Window Focusing Solved**
- Hammerspoon GitHub issue #3276 workaround works
- `hs.window.filter` with `setCurrentSpace(false)` finds cross-space windows
- Direct `window:focus()` switches spaces cleanly without Mission Control

## Minimal Requirements

### 1. Universal Window Detection
- No app-specific hardcoded logic
- Use process tree to find originating window
- Works for any application (VS Code, Terminal, IntelliJ, etc.)

### 2. Smart Focus Detection  
- Only notify when user has switched away from originating window
- Simple: current focused app ≠ originating app

### 3. Simple Notification
- macOS native notification with click handler
- Click → focus original window (using Hammerspoon breakthrough)
- Message: "Claude Code finished in [project]"

### 4. Claude Code Integration
- Single Python script triggered by Claude Code hooks
- Parse JSON input from hooks
- Fast execution (<100ms)

## Implementation Plan

**Phase 1: Core Script** ⏳
- Python script that uses Hammerspoon for cross-space focusing
- Universal window detection (no app-specific code)
- Basic notification delivery

**Phase 2: Claude Integration** ⏳  
- Hook into Claude Code notification/completion events
- JSON parsing and context extraction
- Performance optimization

**Phase 3: Polish** ⏳
- Error handling and fallbacks
- Testing and validation

## Success Criteria
- Works universally (any app, any space)
- Fast and reliable
- Simple codebase (not like legacy shell scripts)
- True click-to-focus across spaces

---
*Surgical, minimal, universal - leveraging the Hammerspoon breakthrough*