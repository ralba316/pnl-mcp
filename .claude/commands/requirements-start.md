# Start Requirements Gathering

Begin systematic requirements gathering for a new feature or project.

## Aliases:
- `/requirements-start`
- `/start`
- `/begin`

## Usage:
`/requirements-start [brief description of requirement]`

## Process Overview:

### Phase 1: Initial Setup & Codebase Analysis
1. Create timestamped requirement folder
2. Initialize tracking files and metadata
3. Analyze existing codebase architecture
4. Document initial findings

### Phase 2: Context Discovery Questions (5-8 questions)
- What functionality is needed?
- Who are the users?
- How will it integrate with existing features?
- What are the core workflows?

### Phase 3: Targeted Context Gathering
- Examine relevant codebase sections
- Identify existing patterns and conventions
- Document technical constraints
- Note architectural decisions

### Phase 4: Expert Requirements Questions (8-12 questions)
- Edge cases and error handling
- Performance and scalability needs
- Security and validation requirements  
- Business rules and constraints

### Phase 5: Requirements Documentation
- Generate comprehensive specification
- Include functional and technical requirements
- Provide implementation guidance
- Create acceptance criteria

## Execution Steps:

1. **Folder Creation:**
   ```
   requirements/YYYY-MM-DD-HHMM-[requirement-slug]/
   ├── metadata.json
   ├── discovery-questions.md
   ├── discovery-answers.md
   ├── context-findings.md
   ├── expert-questions.md
   ├── expert-answers.md
   └── requirements-specification.md (generated at end)
   ```

2. **Metadata Structure:**
   ```json
   {
     "id": "2025-01-26-1400-profile-upload",
     "name": "profile-picture-upload",
     "description": "Add profile picture upload feature",
     "status": "in_progress",
     "phase": "discovery",
     "started_at": "2025-01-26T14:00:00Z",
     "questions_answered": 0,
     "total_questions": 5
   }
   ```

3. **Set Active Requirement:**
   Create/update `requirements/.current-requirement` with folder name

4. **Initial Codebase Analysis:**
   - Framework and architecture overview
   - Relevant existing features
   - Data models and API patterns
   - Authentication and authorization
   - File structure and conventions

5. **Begin Discovery Questions:**
   Start with first contextual question focused on understanding the requirement scope and user needs.

## Question Guidelines:
- One question at a time
- Yes/No format with smart defaults
- Wait for response before continuing
- Document all answers systematically
- Move through phases sequentially

## Success Criteria:
- Complete requirements specification document
- All phases completed systematically  
- Technical approach clearly defined
- Implementation ready with clear acceptance criteria