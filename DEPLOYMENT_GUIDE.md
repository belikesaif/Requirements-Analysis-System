# Deployment Guide for NLP Requirements Analysis System

## Overview
This guide will help you deploy your application using free tier services:
- **Backend**: Deploy to Render (FastAPI/Python)
- **Frontend**: Deploy to Vercel (React)

## Prerequisites
- Git repository (✓ Already set up)
- GitHub account
- Render account (free)
- Vercel account (free)

## Backend Deployment (Render)

### Step 1: Push to GitHub
```bash
# Add and commit all changes
git add .
git commit -m "Add deployment configuration"
git push origin NRAS-57-FL
```

### Step 2: Deploy to Render
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `Requirements-Analysis-System`
4. Select the `backend` folder as the root directory
5. Configure the service:
   - **Name**: `nlp-requirements-backend`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: `3.11.0`

### Step 3: Set Environment Variables in Render
Add these environment variables in the Render dashboard:
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: `gpt-4o-mini`
- `RESEARCH_MODE`: `true`
- `EXPORT_FORMAT`: `json`
- `API_HOST`: `0.0.0.0`
- `FRONTEND_URL`: `https://your-app-name.vercel.app` (update after frontend deployment)
- `RESEARCH_DATA_PATH`: `./research_data`
- `AUTO_SAVE`: `true`
- `LOG_LEVEL`: `INFO`
- `LOG_FILE`: `app.log`

## Frontend Deployment (Vercel)

### Step 1: Build the Frontend
```bash
cd frontend
npm install
npm run build
```

### Step 2: Deploy to Vercel (CLI Method)
```bash
# Login to Vercel
vercel login

# Deploy from frontend directory
cd frontend
vercel --prod
```

### Step 3: Set Environment Variables
After deployment, set the environment variable:
```bash
vercel env add REACT_APP_API_URL
# Enter: https://your-backend-app.onrender.com/api
```

### Alternative: Deploy via Vercel Dashboard
1. Go to [vercel.com](https://vercel.com) and login
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Set root directory to `frontend`
5. Add environment variable:
   - `REACT_APP_API_URL`: `https://your-backend-app.onrender.com/api`

## Post-Deployment Steps

### 1. Update Backend CORS
After frontend deployment, update the backend environment variable:
- `FRONTEND_URL`: `https://your-app-name.vercel.app`

### 2. Test the Deployment
1. Visit your frontend URL
2. Try uploading a requirements document
3. Check if AI processing works
4. Verify diagram generation

## Troubleshooting

### Backend Issues
- Check Render logs for errors
- Verify all environment variables are set
- Ensure OpenAI API key is valid

### Frontend Issues
- Check browser console for errors
- Verify API URL is correct
- Check network tab for failed requests

### CORS Issues
- Ensure frontend URL is added to backend CORS settings
- Restart backend service after CORS changes

## Free Tier Limitations
- **Render**: 512MB RAM, sleeps after 15 minutes of inactivity
- **Vercel**: 100GB bandwidth/month, 1000 serverless function invocations

## Monitoring
- Monitor usage in both Render and Vercel dashboards
- Set up alerts for approaching limits
- Consider upgrading if needed

## URLs After Deployment
- Backend: `https://your-backend-app.onrender.com`
- Frontend: `https://your-app-name.vercel.app`
- API Docs: `https://your-backend-app.onrender.com/docs`
