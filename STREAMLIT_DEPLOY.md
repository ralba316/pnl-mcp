# Streamlit Cloud Deployment Guide

## Step-by-Step Deployment

### 1. Sign in to Streamlit Cloud
- Go to: https://share.streamlit.io
- Click "Sign in"
- Sign in with your GitHub account: **ralba316**

### 2. Make Repository Public (if private)
Your app must be in a public repository OR you need to grant Streamlit access to private repos.

To check/make public:
1. Go to: https://github.com/ralba316/pnl-mcp/settings
2. Scroll to "Danger Zone"
3. If repository is private, click "Change visibility" → "Make public"

### 3. Deploy the App

**Option A: Deploy from Streamlit Cloud Dashboard**
1. Go to: https://share.streamlit.io
2. Click "New app" button
3. Fill in:
   - **Repository**: `ralba316/pnl-mcp`
   - **Branch**: `streamlit` ← **IMPORTANT: Use streamlit branch!**
   - **Main file path**: `dashboard.py`
4. Click "Deploy"

**Option B: Use Direct Deploy URL**
Click this link (replace YOUR_GITHUB_USERNAME if needed):
```
https://share.streamlit.io/ralba316/pnl-mcp/streamlit/dashboard.py
```

### 4. Wait for Deployment
- First deployment takes 2-5 minutes
- You'll see the build logs
- Once complete, you'll get a URL like: `https://pnl-mcp-xxxxx.streamlit.app`

### 5. Troubleshooting

**"You do not have access to this app"**
- Repository is private → Make it public or grant Streamlit access
- Not signed in → Sign in with GitHub account that owns the repo
- Wrong branch → Make sure you selected `streamlit` branch

**Build fails**
- Check the logs for specific errors
- Verify `requirements.txt` is present
- Verify `data_files/pnl_data.xlsx` exists in the branch

**App runs but shows errors**
- Check if data file loaded correctly
- Review Streamlit Cloud logs for Python errors

## Current Configuration

**Repository**: https://github.com/ralba316/pnl-mcp
**Branch**: streamlit
**Main File**: dashboard.py
**Python Version**: 3.11

All required files are in the `streamlit` branch:
- ✅ dashboard.py
- ✅ requirements.txt
- ✅ data_files/pnl_data.xlsx
- ✅ .streamlit/config.toml
- ✅ packages.txt

## Local Testing

Before deploying, test locally:
```bash
streamlit run dashboard.py
```

Should open at: http://localhost:8501
