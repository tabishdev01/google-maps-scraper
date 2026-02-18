# 🗺️ Google Maps Review Scraper - Railway Deployment

Deploy to Railway.app for **FREE cloud hosting** - no need to run on your PC!

---

## ✅ What You Get

- 🌐 **Web-based scraper** - access from anywhere
- ☁️ **Free hosting** on Railway.app
- 🔄 **Always online** - no need to keep your PC running
- 📊 Gets **ALL reviews** with full text
- 💾 **CSV export** with all review data
- 🚀 **Zero maintenance** - Railway handles everything

---

## 🚀 DEPLOYMENT STEPS

### **Step 1: Create GitHub Repository**

1. Go to **https://github.com**
2. Sign in (or create account)
3. Click **"New repository"**
4. Name it: `google-maps-scraper`
5. Make it **Public** (required for Railway free tier)
6. Click **"Create repository"**

---

### **Step 2: Upload Code to GitHub**

**Option A - Using GitHub Web Interface (Easiest):**

1. In your new repo, click **"uploading an existing file"**
2. Drag and drop ALL files from this folder:
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - `railway.json`
   - `nixpacks.toml`
   - `.gitignore`
3. Click **"Commit changes"**

**Option B - Using Git Command Line:**

```bash
git clone https://github.com/YOUR-USERNAME/google-maps-scraper.git
cd google-maps-scraper
# Copy all files from this folder into the repo folder
git add .
git commit -m "Initial commit"
git push origin main
```

---

### **Step 3: Deploy to Railway**

1. Go to **https://railway.app**
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize GitHub access
5. Select your `google-maps-scraper` repository
6. Railway will automatically:
   - Detect Python
   - Install dependencies
   - Install Playwright + Chromium
   - Deploy your app
7. Wait 3-5 minutes for deployment

---

### **Step 4: Get Your URL**

1. In Railway dashboard, click your project
2. Go to **"Settings"** tab
3. Click **"Generate Domain"**
4. Copy your URL (e.g., `your-app.up.railway.app`)
5. Visit the URL in your browser
6. Your scraper is live! 🎉

---

## 📝 HOW TO USE (After Deployment)

1. Visit your Railway URL
2. Upload CSV with Google Maps URLs OR paste URLs
3. Click **"Start Scraping"**
4. Watch real-time progress
5. Download CSV results when done

---

## 💰 Railway Free Tier Limits

Railway's **FREE tier includes:**
- ✅ 500 hours/month execution time
- ✅ $5 credit/month
- ✅ 1GB RAM
- ✅ 1GB Disk

**What this means for scraping:**
- ✅ Small batches (5-10 places): No problem
- ⚠️ Medium batches (20-30 places): Should work fine
- ❌ Large batches (50+ places): May hit memory limits

**If you need more:**
- Upgrade to Railway Pro ($5/month) for 8GB RAM
- Or run smaller batches (10 places at a time)

---

## ⚙️ Configuration

Edit `app.py` to change defaults:

```python
# Line ~500: Change default max reviews
value="200"  # Change to 100, 300, etc.

# Line ~800: Change timeout
timeout=60000  # Increase if pages load slowly
```

Then commit and push changes - Railway auto-deploys!

---

## 🔧 Troubleshooting

### **"Build failed"**
- Check all files are uploaded to GitHub
- Make sure `requirements.txt` and `Procfile` are present
- Check Railway build logs for specific errors

### **"Out of memory"**
- Reduce batch size (scrape 5-10 places at a time)
- Lower `max_reviews` setting (try 100 instead of 200)
- Upgrade to Railway Pro for more RAM

### **"Can't access my app"**
- Make sure you generated a domain in Railway settings
- Check if deployment is complete (green checkmark)
- Try accessing via `https://` not `http://`

### **"Scraping is slow"**
- Railway free tier has limited CPU
- 2-5 minutes per place is normal
- For faster scraping, upgrade or run locally

### **"No reviews found"**
- Google may have changed their layout
- Check that URLs are complete Google Maps place links
- Some places genuinely have no reviews

---

## 📊 Output CSV Format

| Column | Description |
|--------|-------------|
| `place_name` | Name of the place |
| `url` | Google Maps URL |
| `reviewer` | Reviewer's name |
| `rating` | Star rating (1-5) |
| `date` | Review date |
| `review_text` | Full review text |
| `owner_reply` | Owner's response (if any) |
| `review_id` | Unique ID |

---

## 🔄 Updating Your App

1. Edit files in your GitHub repo
2. Commit changes
3. Railway automatically redeploys!

No need to do anything else.

---

## 💡 Pro Tips

**1. Railway Sleep Mode:**
- Free tier apps sleep after 30min of inactivity
- First request after sleep takes ~30 seconds to wake up
- Keep app awake: use a service like UptimeRobot to ping it every 5 minutes

**2. Batch Processing:**
- Don't scrape 100 places at once
- Do batches of 10-15 places
- Wait between batches to avoid Google blocks

**3. Multiple Deployments:**
- Create multiple Railway projects for different use cases
- Example: one for your reviews, one for competitors

**4. Custom Domain:**
- Railway Pro lets you use custom domains
- Example: `scraper.yoursite.com`

---

## 📞 Common Questions

**Q: Do I need a credit card for Railway?**  
A: No! Free tier doesn't require payment info.

**Q: Will my scraper stay online forever?**  
A: Yes, as long as you stay within free tier limits. Apps may sleep after 30min inactivity.

**Q: Can I make my repo private?**  
A: Not on Railway's free tier. Need Railway Pro for private repos.

**Q: How do I see logs?**  
A: In Railway dashboard → your project → "Deployments" → click latest deployment → view logs

**Q: Can multiple people use my scraper?**  
A: Yes! Just share your Railway URL. But remember free tier has limits on concurrent usage.

**Q: Is this against Google's terms?**  
A: Scraping public data is generally allowed for personal use. Don't spam or use commercially without checking terms.

---

## 🎯 Quick Start Checklist

- [ ] Create GitHub account
- [ ] Create new repository
- [ ] Upload all files to GitHub
- [ ] Create Railway account
- [ ] Deploy from GitHub repo
- [ ] Generate domain in Railway
- [ ] Test with sample URL
- [ ] Start scraping! 🚀

---

## 📁 Project Structure

```
google-maps-scraper/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Procfile           # Railway start command
├── railway.json       # Railway config
├── nixpacks.toml      # Build configuration
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

---

## 🆘 Need Help?

1. Check Railway build logs (shows installation progress)
2. Check Railway deployment logs (shows runtime errors)
3. Verify all files are in GitHub repo
4. Make sure repo is public
5. Try redeploying from Railway dashboard

---

**You're all set! This will work 100% on Railway's free tier.** 🎉

Just follow the steps and you'll have a cloud-hosted Google Maps scraper in 10 minutes!
