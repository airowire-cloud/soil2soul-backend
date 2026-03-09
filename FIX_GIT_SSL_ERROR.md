# Fix: SSL Certificate Error with GitHub

## ⚠️ Problem
```
fatal: unable to access 'https://github.com/...': SSL certificate problem: 
self-signed certificate in certificate chain
```

---

## ✅ Solution 1: Disable SSL Verification (Quick Fix)

**⚡ Fastest way for development/testing:**

```bash
# Disable SSL verification ONLY for this push
git push https://github.com/YOUR_USERNAME/soil-soul-frontend.git main --no-verify

# Or set globally (not recommended for security)
git config --global http.sslVerify false
git push -u origin main
```

---

## ✅ Solution 2: Use SSH Instead of HTTPS (Recommended)

### Step 1: Generate SSH Key

```bash
# Generate SSH key (press Enter 3 times to skip password)
ssh-keygen -t rsa -b 4096

# Output shows: Your identification has been saved in C:\Users\YOUR_USERNAME\.ssh\id_rsa
```

### Step 2: Copy SSH Key

```bash
# Display your public key (copy this)
cat ~/.ssh/id_rsa.pub

# Or on Windows PowerShell:
Get-Content ~/.ssh/id_rsa.pub | Set-Clipboard
```

### Step 3: Add Key to GitHub

1. Go to https://github.com/settings/keys
2. Click **New SSH key**
3. **Title**: "My Laptop"
4. **Key**: Paste your public key (from Step 2)
5. Click **Add SSH key**

### Step 4: Update Git Remote

```bash
# Remove HTTPS remote
git remote remove origin

# Add SSH remote
git remote add origin git@github.com:YOUR_USERNAME/soil-soul-frontend.git

# Push
git push -u origin main
```

---

## ✅ Solution 3: Update Git Certificates

### Option A: Download Latest Certificates

```bash
# Windows PowerShell (as Administrator):
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Install latest Git
# Go to https://git-scm.com/download/win
# Download and install latest version
```

### Option B: Use Git's Built-in SSL

```bash
# Tell Git to use Windows Certificate Store
git config --global http.sslBackend schannel
git push -u origin main
```

---

## ✅ Solution 4: Corporate Proxy Issue

If you're behind a corporate firewall:

```bash
# Set proxy
git config --global http.proxy http://proxy-server:port

# Example:
git config --global http.proxy http://corporate-proxy.com:8080

# Try push again
git push -u origin main

# If it fails, disable SSL verification for this push only:
git -c http.sslVerify=false push -u origin main
```

---

## 🔧 Complete Step-by-Step Fix

### Try These In Order:

**Step 1: Use SSH (BEST)**
```bash
# Generate key
ssh-keygen -t rsa -b 4096

# Copy public key
cat ~/.ssh/id_rsa.pub

# Add to GitHub: https://github.com/settings/keys

# Update remote
git remote remove origin
git remote add origin git@github.com:YOUR_USERNAME/soil-soul-frontend.git

# Push
git push -u origin main
```

**Step 2: If SSH doesn't work, use HTTPS with SSL disabled (for development only)**
```bash
# Push with SSL verification disabled
git -c http.sslVerify=false push -u origin main
```

**Step 3: If both fail, update Git**
```bash
# Download and install: https://git-scm.com/download/win
# Then try again
```

---

## 📋 For Your Specific Scenario

Run these commands in order:

```powershell
# 1. Navigate to your frontend folder
cd "C:\Users\ShivanandPoojar\OneDrive - AIROWIRE NETWORKS PRIVATE LIMITED\Documents\soil2soul\frontend"

# 2. Try SSH first (recommended)
git remote remove origin
git remote add origin git@github.com:Airowire-team/soilandsoul.git
git push -u origin main

# If SSH fails, try:
# 3. Use HTTPS with SSL disabled
git remote remove origin
git remote add origin https://github.com/Airowire-team/soilandsoul.git
git -c http.sslVerify=false push -u origin main
```

---

## 🔍 Verify Your Setup

```bash
# Check current remote
git remote -v

# Should show:
# origin  git@github.com:Airowire-team/soilandsoul.git (for SSH)
# OR
# origin  https://github.com/Airowire-team/soilandsoul.git (for HTTPS)
```

---

## ❌ Common Issues & Fixes

**"Permission denied (publickey)"**
- SSH key not added to GitHub
- Solution: Go to https://github.com/settings/keys and add your public key

**"Connection timed out"**
- Firewall blocking GitHub
- Solution: Try HTTPS instead of SSH, or contact IT department

**"Authentication failed"**
- Wrong GitHub credentials
- Solution: Use personal access token instead of password

---

## ✅ Recommended: Use Personal Access Token (PAT)

### Generate Token:

1. Go to https://github.com/settings/tokens
2. Click **Generate new token** → **Generate new token (classic)**
3. **Note**: GIT_PUSH_SOIL_AND_SOUL
4. **Expiration**: 90 days
5. **Scope**: Check ✅ `repo`
6. Click **Generate token**
7. **Copy token** (looks like: `ghp_xxxxxxxxxxxx`)

### Use Token:

```bash
# When pushing, use token as password:
git remote remove origin
git remote add origin https://github.com/Airowire-team/soilandsoul.git

# Git will ask for username and password
# Username: your-github-username
# Password: ghp_xxxxxxxxxxxx (your token)

git push -u origin main
```

---

## 🚀 Quickest Solution Right Now

**For immediate deployment:**

```bash
# Option 1: SSH (most secure)
git remote set-url origin git@github.com:Airowire-team/soilandsoul.git
git push -u origin main

# Option 2: HTTPS with SSL disabled (if SSH fails)
git remote set-url origin https://github.com/Airowire-team/soilandsoul.git
git -c http.sslVerify=false push -u origin main

# Option 3: GitHub CLI (if you have it installed)
gh repo clone Airowire-team/soilandsoul
cd soilandsoul
git add .
git commit -m "Push from local"
git push
```

---

## ✅ Next: Verify Push Succeeded

```bash
# Confirm push worked
git log --oneline -n 5

# Go to https://github.com/Airowire-team/soilandsoul
# You should see your commits
```

---

## 📞 If Still Having Issues

Try this diagnostic:

```bash
# Test GitHub connectivity
git config --list | grep http

# Test SSL:
curl https://github.com

# If curl fails, your firewall/proxy is blocking HTTPS
# Contact your IT department
```

---

**Choose Solution 1 (SSH) or Solution 2 (HTTPS with token) - they're both secure and will work! ✅**
