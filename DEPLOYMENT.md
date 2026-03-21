# Django Youth Camp Management System - Deployment Guide

## Project Structure
- **Project Name**: basaycamp_project
- **Main App**: youthcamp
- **Database**: SQLite (for now)

## Files Created for Deployment

### 1. requirements.txt
```
Django==4.2.7
gunicorn==21.2.0
whitenoise==6.6.0
```

### 2. build.sh
Build script that runs on Render to:
- Install dependencies
- Run migrations
- Collect static files

### 3. Procfile
Tells Render how to run the application:
```
web: gunicorn basaycamp_project.wsgi:application --bind 0.0.0.0:$PORT
```

### 4. .gitignore
Excludes unnecessary files from Git

### 5. Updated settings.py
- Environment variable support
- WhiteNoise middleware for static files
- Production-ready configuration

## Step-by-Step Deployment Instructions

### Step 1: Push to GitHub

1. **Initialize Git Repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Ready for deployment"
   ```

2. **Create GitHub Repository**:
   - Go to https://github.com
   - Click "New repository"
   - Name: `basaycamp-youth-management` (or your preferred name)
   - Make it Public (Render free tier requires public repos)
   - Don't initialize with README (you already have one)

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/yourusername/basaycamp-youth-management.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Render

1. **Sign up for Render**:
   - Go to https://render.com
   - Sign up with your GitHub account (free)

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select your `basaycamp-youth-management` repository
   - Click "Connect"

3. **Configure the Service**:
   - **Name**: `basaycamp-youth-management`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn basaycamp_project.wsgi:application --bind 0.0.0.0:$PORT`

4. **Add Environment Variables**:
   Click "Environment" tab and add:
   - `SECRET_KEY`: Generate a new secret key (use: https://djecrety.ir/)
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `your-app-name.onrender.com`

5. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment to complete (2-3 minutes)

### Step 3: Post-Deployment Setup

1. **Create Superuser**:
   - Once deployed, go to `https://your-app-name.onrender.com/admin`
   - You'll need to create a superuser:
     - In Render dashboard, click your service → "Shell"
     - Run: `python manage.py createsuperuser`
     - Follow prompts to create admin user

2. **Test the Application**:
   - Visit your app at `https://your-app-name.onrender.com`
   - Test login, add participants, etc.

## Important Notes

### Database
- Currently using SQLite (file-based)
- For production, consider PostgreSQL (Render has free tier)
- To switch to PostgreSQL later:
  - Add `psycopg2-binary` to requirements.txt
  - Update DATABASES settings in settings.py
  - Set DATABASE_URL environment variable

### Environment Variables
- `SECRET_KEY`: Must be unique and secret
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Your Render domain

### Static Files
- WhiteNoise handles static files automatically
- Files are collected to `staticfiles/` directory
- No additional configuration needed

### Troubleshooting

**If deployment fails**:
1. Check Render logs for errors
2. Ensure all files are committed to Git
3. Verify build.sh has execute permissions

**If static files don't load**:
1. Check WhiteNoise is in MIDDLEWARE (first position)
2. Verify STATIC_ROOT is set correctly
3. Run collectstatic manually in Render shell

**If database errors occur**:
1. Run migrations in Render shell: `python manage.py migrate`
2. Check DATABASE_URL environment variable

## Next Steps (Optional)

1. **Add PostgreSQL database** (more robust than SQLite)
2. **Set up custom domain** (if you have one)
3. **Configure email** for notifications
4. **Add monitoring/logging**

## Support

If you encounter issues:
1. Check Render documentation: https://render.com/docs
2. Review deployment logs in Render dashboard
3. Ensure your local environment matches production
