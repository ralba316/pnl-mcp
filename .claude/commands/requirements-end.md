# End Requirements Gathering

Complete the current requirement gathering session with specification generation.

## Aliases:
- `/requirements-end`
- `/end`
- `/finish`

## Instructions:

1. Read requirements/.current-requirement
2. If no active requirement:
   - Show: "No active requirement to end"
   - Exit

3. Show current status and options:
```
📋 Ending: [requirement-name]
Progress: [X/Y] questions in [phase]

Choose completion option:
1. 📄 Generate specification (recommended)
2. ⚠️ Mark as incomplete  
3. 🗑️ Cancel and delete
```

## Option 1: Generate Specification
1. Read all gathered data:
   - discovery-questions.md & answers
   - context-findings.md
   - expert-questions.md & answers
   - metadata.json

2. Create requirements-specification.md:
```markdown
# [Requirement Name] - Requirements Specification

## Overview
[Generated from initial request and context]

## Functional Requirements
[From discovery and expert questions]

## Technical Requirements  
[From codebase analysis and technical findings]

## Implementation Approach
[Suggested based on existing architecture]

## Assumptions & Constraints
[From question responses and analysis]

## Acceptance Criteria
[Specific testable conditions]

## Implementation Notes
[Technical considerations and recommendations]
```

3. Update metadata.json:
   - status: "complete"
   - completed_at: timestamp
   - questions_answered: count
   - specification_generated: true

4. Clear .current-requirement
5. Show completion message with file locations

## Option 2: Mark Incomplete
1. Update metadata.json:
   - status: "incomplete"
   - paused_at: timestamp
   - reason: user input

2. Keep all files for later resumption
3. Clear .current-requirement
4. Show paused message

## Option 3: Cancel & Delete
1. Confirm deletion
2. Remove entire requirement folder
3. Clear .current-requirement
4. Show deletion confirmation