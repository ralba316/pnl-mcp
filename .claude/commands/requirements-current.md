# View Current Requirement

Show complete details of the active requirement with all gathered information.

## Aliases:
- `/requirements-current`
- `/current`
- `/c`

## Instructions:

1. Read requirements/.current-requirement to get active ID
2. If no active requirement:
   - Show: "No active requirement"
   - Suggest: "/requirements-start [description]" or "/requirements-list"
   - Exit

3. If active requirement exists:
   - Read requirement folder contents
   - Display comprehensive status

## Display Format:
```
📋 Current Requirement: profile-picture-upload
Duration: 45 minutes | Phase: Expert Requirements (4/5)

📝 Initial Request:
"Add profile picture upload feature with validation"

🔍 Codebase Overview:
- Framework: Next.js 14 with TypeScript
- Auth: NextAuth.js with session management
- File handling: No existing image processing
- Database: Prisma with PostgreSQL

🎯 Context Discovery (Complete):
✅ User upload interface needed (Yes)
✅ File validation required (Yes) 
✅ Image processing needed (Yes)
✅ Storage solution needed (AWS S3)
✅ Database schema changes (User.profileImage)

🔧 Technical Findings:
- Need to add multer for file handling
- Sharp for image processing/resizing
- AWS SDK configuration required
- Database migration for profile_image column

📊 Expert Requirements Progress (4/8):
✅ Q1: Multiple file format support? (Yes - JPG, PNG, WebP)
✅ Q2: Maximum file size limit? (5MB default, Yes)
✅ Q3: Image compression required? (Yes - auto-optimize)
✅ Q4: Profile image dimensions? (150x150 square crop)
❓ Q5: Replace existing or keep history?
❓ Q6: Admin moderation features needed?
❓ Q7: Integration with existing avatar system?
❓ Q8: Fallback for failed uploads?
```

## View Options:
- Continue: "/requirements-status" 
- End session: "/requirements-end"
- View all: "/requirements-list"