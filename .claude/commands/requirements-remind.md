# Requirements Reminder

Provide process reminders and guidelines during requirements gathering.

## Aliases:
- `/requirements-remind`
- `/remind`  
- `/r`

## Auto-Trigger Patterns:
- When jumping ahead in phases too quickly
- When asking implementation questions during discovery
- When user provides vague or unclear responses
- When breaking established question format

## Reminder Template:

```
🔄 Requirements Process Reminder

Current Phase: [Discovery/Expert Requirements]
Progress: [X/Y] questions

📋 Phase Guidelines:
[Phase-specific rules and expectations]

❓ Question Format:
- One focused yes/no question
- Include smart default in parentheses
- Wait for clear response before continuing

⚠️ Common Issues to Avoid:
- Jumping to implementation details
- Asking multiple questions at once
- Accepting vague responses
- Skipping systematic discovery

💡 Current Focus:
[What should be happening right now]
```

## Phase-Specific Reminders:

### Context Discovery Phase:
```
🔍 Discovery Phase Guidelines:
- Focus on WHAT needs to be built
- Identify core functionality
- Understand user workflows
- Map existing system touchpoints
- Ask broad, exploratory questions
- Avoid technical implementation details
```

### Targeted Context Phase:
```
🎯 Context Gathering:
- Analyze discovered requirements
- Examine relevant codebase sections
- Document existing patterns
- Identify technical constraints
- Note architectural decisions
- Prepare for expert questions
```

### Expert Requirements Phase:
```
🔬 Expert Requirements:
- Ask specific, technical questions
- Focus on edge cases and constraints
- Clarify business rules
- Define acceptance criteria
- Consider performance implications
- Address security requirements
```

## Correction Scenarios:

### User Jumping Ahead:
```
⏸️ Hold on! We're still in [current phase].

Before moving to implementation, we need to complete the systematic requirements gathering. This ensures we don't miss critical details.

Let's continue with: [next question]
```

### Vague Response:
```
🤔 Need a clearer answer for proper documentation.

Question: [repeat question]
Please respond with: Yes, No, or "I don't know"
Default assumption: [default]
```

### Breaking Question Format:
```
📝 Sticking to the structured format helps ensure complete coverage.

One question at a time with yes/no responses helps us:
- Document decisions clearly  
- Avoid missed requirements
- Build comprehensive specifications
```

## Process Benefits Reminder:
- Systematic coverage prevents missed requirements  
- Clear documentation enables better implementation
- Structured approach reduces rework and scope creep
- Expert questions catch edge cases early