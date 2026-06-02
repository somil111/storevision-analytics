# How to Push StoreVision to GitHub

Complete step-by-step guide to push your project to GitHub.

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Enter repository name: `storevision-analytics`
3. Choose visibility: **Public** (so anyone can access)
4. Add description: "Production-grade CCTV intelligence system with real-time analytics"
5. Do NOT initialize with README (we have our own)
6. Click "Create repository"

## Step 2: Setup Git Locally

Open PowerShell in your project root directory:

```powershell
cd "c:\Users\somil\OneDrive\Desktop\offline store cctv prediction system\storevision_platform"
```

Initialize git repository:

```powershell
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## Step 3: Add All Files

Stage all files for commit:

```powershell
git add .
```

Verify what will be committed:

```powershell
git status
```

You should see all files except those in `.gitignore`.

## Step 4: Make Initial Commit

```powershell
git commit -m "Initial commit: StoreVision Analytics Platform v1.0.0"
```

## Step 5: Add Remote Repository

Replace `yourusername` with your GitHub username:

```powershell
git remote add origin https://github.com/yourusername/storevision-analytics.git
```

Verify remote was added:

```powershell
git remote -v
```

## Step 6: Push to GitHub

Push your code to GitHub:

```powershell
git branch -M main
git push -u origin main
```

The `-u` flag sets the upstream branch so future pushes are simpler.

## Step 7: Verify on GitHub

1. Go to https://github.com/yourusername/storevision-analytics
2. Verify all files are there
3. Check README displays properly
4. Verify project structure matches local

## Complete Commands (Copy & Paste)

```powershell
cd "c:\Users\somil\OneDrive\Desktop\offline store cctv prediction system\storevision_platform"

git init
git config user.name "Your Name"
git config user.email "your.email@example.com"

git add .
git status

git commit -m "Initial commit: StoreVision Analytics Platform v1.0.0"

git remote add origin https://github.com/yourusername/storevision-analytics.git
git remote -v

git branch -M main
git push -u origin main
```

## Files Included in Push

### Essential Files
```
storevision_platform/
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── video_processor.py
│   ├── event_stream.py
│   ├── analytics_engine.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── README.md
├── QUICKSTART.md
├── SYSTEM_OVERVIEW.md
├── FEATURES.md
├── PROJECT_STRUCTURE.md
├── DEPLOYMENT.md
├── CONTRIBUTING.md
├── LICENSE
├── Dockerfile
├── docker-compose.yml
└── .gitignore
```

### NOT Included (in .gitignore)
```
__pycache__/
*.pyc
*.egg-info/
.venv/
uploads/
.env
.DS_Store
```

## After Initial Push

### Making Updates

After initial push, making changes is simpler:

```powershell
git add .
git commit -m "Description of changes"
git push
```

### Creating Feature Branches

For new features:

```powershell
git checkout -b feature/your-feature-name
# Make changes
git add .
git commit -m "[FEATURE] Add your feature"
git push -u origin feature/your-feature-name
# Create Pull Request on GitHub
```

### Creating Bug Fix Branches

For bug fixes:

```powershell
git checkout -b bugfix/issue-name
# Fix the bug
git add .
git commit -m "[BUGFIX] Fix issue description"
git push -u origin bugfix/issue-name
# Create Pull Request on GitHub
```

## GitHub Features to Enable

### 1. Enable GitHub Pages (Optional)

For documentation site:
1. Go to repository Settings
2. Scroll to "Pages"
3. Select "main branch" as source
4. Documentation will be available at: https://yourusername.github.io/storevision-analytics

### 2. Enable Issues

Allow users to report bugs:
1. Go to Settings
2. Ensure "Issues" is checked
3. Add issue templates for bugs and features

### 3. Enable Discussions

Allow community Q&A:
1. Go to Settings
2. Enable "Discussions"
3. Create categories for Q&A and announcements

### 4. Setup Branch Protection

Protect main branch:
1. Go to Settings > Branches
2. Add rule for "main"
3. Require pull request reviews
4. Require status checks (CI/CD)

### 5. Enable Deployments

Setup automatic deployments:
1. Go to Settings > Environments
2. Add "production" environment
3. Configure deployment rules

## Sample README for GitHub

Your README.md already includes:

- Project overview
- Quick start guide
- Features list
- Architecture diagram
- Installation instructions
- Usage examples
- API documentation links
- Contributing guidelines
- License information

## GitHub Badges (Optional)

Add to top of README.md:

```markdown
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.9.0-red.svg)](https://opencv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/yourusername/storevision-analytics.svg?style=social)](https://github.com/yourusername/storevision-analytics)
```

## Accessing Your Repository

### View Online
```
https://github.com/yourusername/storevision-analytics
```

### Clone for Others
```bash
git clone https://github.com/yourusername/storevision-analytics.git
cd storevision-analytics
```

### Access Dashboard
```
1. Clone the repository
2. Follow QUICKSTART.md
3. Run: python backend/main.py
4. Open: http://localhost:8000/static/index.html
```

## Next Steps

1. Verify all files on GitHub
2. Update collaborators in Settings
3. Create GitHub Issues for planned features
4. Add project description and topics
5. Enable all optional features (Pages, Discussions, etc.)
6. Share repository with team members
7. Promote in relevant communities

## Troubleshooting

### Authentication Error

If you get authentication error:

```powershell
git remote set-url origin https://github.com/yourusername/storevision-analytics.git
```

Or use personal access token:

```powershell
git remote set-url origin https://<token>@github.com/yourusername/storevision-analytics.git
```

### Large Files

If you have files > 100MB, use Git LFS:

```powershell
git lfs install
git lfs track "*.mp4"
git add .gitattributes
```

### Already Pushed?

Update with new files:

```powershell
git add .
git commit -m "Add missing documentation"
git push
```

## Success!

Your StoreVision Analytics Platform is now on GitHub! Anyone can:

1. View your code
2. Read documentation
3. Clone the repository
4. Run the platform locally
5. Contribute improvements
6. Report issues

Share your repository link and celebrate!

---

**Your Repository URL**:
```
https://github.com/yourusername/storevision-analytics
```

**Dashboard Access Instructions**:
```
1. Clone: git clone https://github.com/yourusername/storevision-analytics.git
2. Install: pip install -r backend/requirements.txt
3. Run: python backend/main.py
4. Open: http://localhost:8000/static/index.html
```
