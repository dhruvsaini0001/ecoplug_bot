# 🚀 Render Deployment Checklist

## Before You Deploy

- [ ] Code is pushed to GitHub/GitLab
- [ ] MongoDB Atlas cluster is set up (or using in-memory sessions)
- [ ] `.env` file is NOT committed (check `.gitignore`)
- [ ] `render.yaml` is configured with correct MongoDB URL

## Deployment Steps

### 1️⃣ Setup MongoDB Atlas (Free)
- [ ] Go to https://www.mongodb.com/cloud/atlas
- [ ] Create a free account
- [ ] Create a new cluster (select Free tier - M0)
- [ ] Create database user (Database Access → Add New User)
- [ ] Whitelist all IPs: Network Access → Add IP → Allow Access from Anywhere (0.0.0.0/0)
- [ ] Get connection string: Clusters → Connect → Connect your application
- [ ] Copy the connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)

### 2️⃣ Update render.yaml
- [ ] Open `render.yaml` 
- [ ] Find the `MONGODB_URL` environment variable
- [ ] Replace `mongodb://localhost:27017` with your MongoDB Atlas connection string
- [ ] Save the file
- [ ] Commit and push to GitHub:
   ```bash
   git add render.yaml
   git commit -m "Configure MongoDB for Render deployment"
   git push
   ```

### 3️⃣ Deploy to Render

#### Option A: Using Blueprint (Recommended)
- [ ] Go to https://dashboard.render.com
- [ ] Sign up / Log in
- [ ] Click "New +" → "Blueprint"
- [ ] Connect your GitHub/GitLab account
- [ ] Select your repository: `ecoplug_bot`
- [ ] Render will detect `render.yaml` automatically
- [ ] Click "Apply"
- [ ] Wait 3-5 minutes for deployment

#### Option B: Manual Setup
- [ ] Go to https://dashboard.render.com
- [ ] Click "New +" → "Web Service"
- [ ] Connect your repository
- [ ] Configure:
  - **Name:** ecoplug-chatbot-api
  - **Runtime:** Python 3
  - **Build Command:** `pip install -r requirements.txt`
  - **Start Command:** `uvicorn chatbot.api.main:app --host 0.0.0.0 --port $PORT`
- [ ] Add environment variables (see DEPLOYMENT.md)
- [ ] Click "Create Web Service"

### 4️⃣ Test Your Deployment
- [ ] Wait for "Live" status in Render dashboard
- [ ] Note your app URL (e.g., `https://ecoplug-chatbot-api.onrender.com`)
- [ ] Test health endpoint: `https://your-app.onrender.com/v1/health`
- [ ] Test API docs: `https://your-app.onrender.com/docs`

### 5️⃣ Test API Endpoints

```bash
# Health Check
curl https://your-app.onrender.com/v1/health

# Create Session
curl -X POST https://your-app.onrender.com/v1/chat/sessions \
  -H "Content-Type: application/json" \
  -d '{"metadata": {"platform": "web", "user_agent": "test"}}'

# Send Message (replace SESSION_ID)
curl -X POST https://your-app.onrender.com/v1/chat/sessions/SESSION_ID/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "My car won't charge"}'
```

## Post-Deployment

### Optional: Add OpenAI Integration
- [ ] Get OpenAI API key from https://platform.openai.com
- [ ] In Render Dashboard → Environment
- [ ] Add: `OPENAI_API_KEY` = `sk-your-key-here`
- [ ] Save changes (will auto-redeploy)

### Optional: Custom Domain
- [ ] Render Settings → Custom Domain
- [ ] Add your domain
- [ ] Update DNS records as instructed
- [ ] Free SSL certificate is auto-provisioned

### Optional: Upgrade Plan
- [ ] Free tier: sleeps after 15 min inactivity
- [ ] Starter ($7/mo): always-on, better performance
- [ ] Render Dashboard → Settings → Plan

## Troubleshooting

### Deployment Failed
- Check Render logs for errors
- Verify `requirements.txt` has all dependencies
- Ensure MongoDB URL is correct

### App Keeps Sleeping
- Free tier limitation - upgrade to Starter plan
- Or use external uptime monitor to ping every 10 minutes

### Can't Connect to MongoDB
- Check MongoDB Atlas Network Access settings
- Ensure 0.0.0.0/0 is whitelisted
- Verify connection string format
- Check database user credentials

### Environment Variables Not Working
- Ensure no quotes around values in Render dashboard
- Use JSON format for arrays: `["*"]` not `"['*']"`
- Re-deploy after changing environment variables

## Resources

- 📖 Full deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- 🌐 Render Dashboard: https://dashboard.render.com
- 🗄️ MongoDB Atlas: https://cloud.mongodb.com
- 📚 Render Docs: https://render.com/docs
- 🔧 API Documentation: https://your-app.onrender.com/docs

## Need Help?

- Check Render logs: Dashboard → Logs tab
- View metrics: Dashboard → Metrics tab
- MongoDB logs: Atlas → Metrics tab
