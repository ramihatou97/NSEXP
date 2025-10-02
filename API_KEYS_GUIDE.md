# 📔 API Keys Configuration Guide for NSSP

This guide explains how to obtain and configure all the API keys for your NSSP deployment.

## 🔐 Required Credentials (You Create These)

### 1. PostgreSQL Database
```bash
POSTGRES_USER=neurosurg_prod              # Choose your username
POSTGRES_PASSWORD=<generated-password>     # Generate strong password
POSTGRES_DB=neurosurgical_knowledge_prod   # Choose your database name
```

**Generate secure password:**
```bash
# Linux/Mac/WSL
openssl rand -base64 32

# Windows PowerShell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})

# Example output: "XK9mP2nL8qR5vT7wY3zB6aD4eF1gH0jS"
```

### 2. Redis Cache
```bash
REDIS_PASSWORD=<generated-password>  # Generate another strong password
REDIS_PORT=6379                      # Default port (usually keep as-is)
```

### 3. Application Secret Key
```bash
SECRET_KEY=<generated-key>  # Used for session encryption
```

**Generate secret key:**
```bash
# Generate a 32+ character key
openssl rand -base64 32
```

---

## 🤖 AI Service API Keys (Optional)

The system works in **mock mode** without these keys, but for production AI features:

### 1. OpenAI API Key
- **Sign up:** https://platform.openai.com/signup
- **Get key:** https://platform.openai.com/api-keys
- **Pricing:** https://openai.com/pricing
- **Free tier:** $5 credit for new accounts
```bash
OPENAI_API_KEY=sk-...
```

### 2. Anthropic (Claude) API Key
- **Sign up:** https://console.anthropic.com/signup
- **Get key:** https://console.anthropic.com/settings/keys
- **Pricing:** https://docs.anthropic.com/claude/docs/models-overview#model-pricing
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Google (Gemini) API Key
- **Sign up:** https://makersuite.google.com/app/apikey
- **Documentation:** https://ai.google.dev/
- **Free tier:** Generous free quota available
```bash
GOOGLE_API_KEY=AIza...
```

### 4. Perplexity API Key
- **Sign up:** https://www.perplexity.ai/settings/api
- **Documentation:** https://docs.perplexity.ai/
- **Pricing:** https://www.perplexity.ai/pro
- **Use case:** Advanced web search for medical literature
```bash
PERPLEXITY_API_KEY=pplx-...
```

---

## 📚 External Service API Keys (Optional)

### 1. PubMed/NCBI E-utilities
- **FREE** - No payment required
- **Register:** https://www.ncbi.nlm.nih.gov/account/
- **Get API Key:** https://www.ncbi.nlm.nih.gov/account/settings/
- **Documentation:** https://www.ncbi.nlm.nih.gov/books/NBK25497/
- **Rate limit:** 3 requests/second without key, 10 requests/second with key

```bash
PUBMED_API_KEY=your-pubmed-api-key
PUBMED_EMAIL=your-email@domain.com  # Required by NCBI
```

### 2. Sentry (Error Tracking)
- **Sign up:** https://sentry.io/signup/
- **Free tier:** 5,000 errors/month
- **Create project:** Choose "Python" for backend
- **Get DSN:** Project Settings → Client Keys (DSN)
```bash
SENTRY_DSN=https://...@sentry.io/...
```

### 3. SMTP Email Service (Optional)
For sending system notifications:

**Option A - Gmail:**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Not regular password!
```
**Note:** Enable 2FA and create App Password: https://support.google.com/accounts/answer/185833

**Option B - SendGrid:**
- **Sign up:** https://signup.sendgrid.com/
- **Free tier:** 100 emails/day
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

---

## 🚀 Quick Setup Example

Here's a complete example `.env` configuration:

```bash
# ===== REQUIRED - You create these =====
# Database (PostgreSQL)
POSTGRES_USER=nssp_prod
POSTGRES_PASSWORD=XK9mP2nL8qR5vT7wY3zB6aD4eF1gH0jS
POSTGRES_DB=neurosurgical_knowledge_prod
POSTGRES_PORT=5432

# Cache (Redis)  
REDIS_PASSWORD=aB3cD4eF5gH6iJ7kL8mN9oP0qR1sT2uV
REDIS_PORT=6379

# Application
SECRET_KEY=wX3yZ4aB5cD6eF7gH8iJ9kL0mN1oP2qR

# ===== OPTIONAL - For AI features =====
# AI Services (leave blank for mock mode)
OPENAI_API_KEY=sk-...your-key...
ANTHROPIC_API_KEY=sk-ant-...your-key...
GOOGLE_API_KEY=AIza...your-key...
PERPLEXITY_API_KEY=pplx-...your-key...

# ===== OPTIONAL - External services =====
# Medical Literature Search
PUBMED_API_KEY=your-pubmed-key
PUBMED_EMAIL=admin@yourhospital.org

# Error Tracking
SENTRY_DSN=https://...@sentry.io/...

# Email Notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=nssp-notifications@yourhospital.org
SMTP_PASSWORD=your-app-specific-password
EMAIL_FROM=nssp-notifications@yourhospital.org
```

---

## 📝 Configuration Priority

1. **Essential (Required)**:
   - PostgreSQL credentials
   - Redis password
   - Secret key

2. **Highly Recommended**:
   - At least one AI API key (OpenAI recommended)
   - PubMed API key (free, improves literature search)

3. **Nice to Have**:
   - Perplexity (advanced web search)
   - Sentry (error tracking)
   - SMTP (email notifications)

---

## 🔒 Security Best Practices

1. **Never commit `.env` to Git**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use strong passwords**
   - Minimum 32 characters
   - Mix of letters, numbers, special characters
   - Different password for each service

3. **Rotate keys periodically**
   - Every 90 days for production
   - Immediately if compromised

4. **Limit API key permissions**
   - Use read-only keys where possible
   - Set usage limits
   - Monitor usage

5. **Store securely in production**
   - Use environment variables
   - Consider secret management tools (AWS Secrets Manager, HashiCorp Vault)
   - Never hardcode in source files

---

## 💡 Tips

- **Start with mock mode**: Deploy first without API keys to test the system
- **Add keys gradually**: Start with one AI provider, add others as needed
- **Monitor usage**: Most APIs have dashboards to track usage and costs
- **Set budgets**: Configure spending limits on paid services
- **Free tiers**: Many services offer generous free tiers sufficient for small deployments

---

## 🆘 Troubleshooting

**API Key Not Working?**
1. Check for extra spaces or quotes
2. Verify key starts with expected prefix (sk-, AIza, etc.)
3. Ensure service is activated in provider dashboard
4. Check API key permissions/scopes
5. Verify billing is set up (even for free tiers)

**Environment Variables Not Loading?**
1. Ensure `.env` file is in project root
2. Restart Docker containers after changes
3. Check file permissions (should be readable)
4. Verify no syntax errors in `.env`

**Rate Limiting Issues?**
1. Add delays between requests
2. Implement exponential backoff
3. Use caching to reduce API calls
4. Consider upgrading to paid tier