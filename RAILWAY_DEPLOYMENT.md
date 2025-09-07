# 🚂 Railway Deployment Guide for EFET School Project

## Prerequisites
- GitHub account
- Railway account (free tier available)
- Your project code pushed to GitHub

## Step-by-Step Deployment

### 1. Prepare Your Repository
Make sure all the files are in your GitHub repository:
- ✅ `requirements.txt`
- ✅ `Procfile`
- ✅ `railway.json`
- ✅ Updated `app.py`
- ✅ Updated `__init__.py` with database configuration

### 2. Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Sign up/Login with GitHub
3. Click "Deploy from GitHub repo"
4. Select your `EFET-School-Project` repository
5. Railway will automatically detect it's a Python project

### 3. Add PostgreSQL Database

1. In your Railway project dashboard, click "Add Service"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically provision a PostgreSQL database
4. The `DATABASE_URL` environment variable will be automatically set

### 4. Configure Environment Variables

In Railway project settings, add these environment variables:
```
SECRET_KEY=your-super-secret-key-change-this
FLASK_ENV=production
```

### 5. Deploy

1. Railway will automatically build and deploy your application
2. You'll get a live URL like `https://your-app-name.railway.app`
3. The database tables will be created automatically on first run

### 6. Access Your Application

- **URL**: Your Railway app URL
- **Admin Login**: 
  - Email: `admin@efet.edu`
  - Password: `admin123` (⚠️ Change this immediately!)

## Important Notes

### 🔒 Security
- Change the admin password immediately after first login
- Update the `SECRET_KEY` to a strong, unique value
- Never commit sensitive data to GitHub

### 💾 Database
- Your SQLite database won't work on Railway
- PostgreSQL database is automatically configured
- Data persists between deployments

### 📁 File Uploads
- File uploads will work but have storage limitations on free tier
- Consider using cloud storage (AWS S3, Cloudinary) for production

### 💰 Costs
- Free tier: $5/month in usage credits
- Typical usage for small school: $2-4/month
- Overage: Pay-as-you-go pricing

## Troubleshooting

### If deployment fails:
1. Check the build logs in Railway dashboard
2. Ensure all dependencies are in `requirements.txt`
3. Verify `Procfile` syntax

### If database connection fails:
1. Verify PostgreSQL service is running
2. Check `DATABASE_URL` environment variable is set
3. Run the migration script manually if needed

### If static files don't load:
1. Verify static file paths use `/static/` prefix
2. Check Railway build logs for static file collection

## Support

For issues specific to:
- **Railway**: Check Railway documentation or support
- **Application**: Review application logs in Railway dashboard
- **Database**: Use Railway PostgreSQL service logs

## Next Steps After Deployment

1. 🔐 Change admin password
2. 👥 Create teacher and student accounts
3. 📚 Add majors and subjects
4. 🎨 Customize school branding
5. 📧 Configure email settings (optional)

Happy deploying! 🚀