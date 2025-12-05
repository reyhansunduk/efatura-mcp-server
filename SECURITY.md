# Security Guidelines

## 🔒 Important Security Information

This MCP server integrates with the Turkish Tax Authority (GİB) e-Fatura system and handles sensitive company credentials. **Please read this document carefully before using in production.**

---

## 🚨 Critical Security Rules

### 1. **NEVER Commit Credentials to Git**

Your `.env` file contains sensitive credentials and **MUST NEVER** be committed to version control.

**✅ Safe:**
```bash
# .env is already in .gitignore
# Copy .env.example to .env and fill in your credentials
cp .env.example .env
```

**❌ Dangerous:**
```bash
# NEVER do this!
git add .env
git commit -m "Add config"  # This exposes your credentials!
```

### 2. **Verify Before Pushing to GitHub**

Before pushing your code to GitHub:

```bash
# Check what files will be committed
git status

# Verify .env is NOT in the list
# If you see .env, DO NOT COMMIT!

# Double-check .gitignore
cat .gitignore | grep ".env"
# Should output: .env
```

### 3. **Use Environment-Specific Credentials**

- **Test Environment:** Use test credentials for development
- **Production Environment:** Use real credentials only on secure servers

```bash
# Development
GIB_ENVIRONMENT=test
GIB_USERNAME=your_test_username
GIB_PASSWORD=your_test_password

# Production (on secure server only)
GIB_ENVIRONMENT=production
GIB_USERNAME=your_real_vkn
GIB_PASSWORD=your_real_password
```

---

## 🔐 Credential Management Best Practices

### Storing Credentials

1. **Local Development:**
   - Store in `.env` file (already in .gitignore)
   - Never share your `.env` file

2. **Production Servers:**
   - Use environment variables
   - Use secret management systems (AWS Secrets Manager, Azure Key Vault, etc.)
   - Never hardcode credentials in source code

3. **Claude Desktop:**
   - Credentials are read from `.env` in your project directory
   - Make sure your `.env` file has restricted permissions

### File Permissions (Linux/Mac)

```bash
# Restrict .env file to owner-only
chmod 600 .env

# Verify permissions
ls -la .env
# Should show: -rw------- (owner read/write only)
```

### File Permissions (Windows)

```powershell
# Remove inherited permissions and grant access only to current user
icacls .env /inheritance:r
icacls .env /grant:r "%USERNAME%:F"
```

---

## 🛡️ Safe GitHub Practices

### Before Creating a Repository

1. **Verify .gitignore is configured:**
   ```bash
   cat .gitignore | grep -E "\.env|credentials|secrets"
   ```

2. **Check for accidentally committed secrets:**
   ```bash
   git log --all --full-history -- .env
   # Should return nothing
   ```

3. **Use .env.example for documentation:**
   - Include `.env.example` with dummy values
   - Add clear instructions
   - Never include real credentials

### .env.example Template

The `.env.example` file should contain:
- ✅ Placeholder values
- ✅ Clear comments
- ✅ Setup instructions
- ❌ NO real credentials

Example:
```bash
# EXAMPLE - Replace with your real credentials
GIB_USERNAME=your_gib_username_here
GIB_PASSWORD=your_gib_password_here
GIB_ENVIRONMENT=test
```

---

## 🚦 Production Deployment Checklist

Before deploying to production:

- [ ] `.env` is in `.gitignore`
- [ ] No credentials in source code
- [ ] Using `GIB_ENVIRONMENT=production`
- [ ] Real credentials stored securely
- [ ] `.env` file has restricted permissions
- [ ] Credentials are not logged
- [ ] HTTPS is used for all API calls
- [ ] Server has proper firewall rules
- [ ] Regular security updates applied

---

## 🔍 Credential Validation

The server includes built-in validation to prevent common mistakes:

```python
# The server will refuse to start with placeholder values
GIB_USERNAME=your_gib_username_here  # ❌ Will fail
GIB_USERNAME=1234567890              # ✅ Will work

GIB_PASSWORD=your_gib_password_here  # ❌ Will fail
GIB_PASSWORD=mySecurePassword123     # ✅ Will work
```

Error messages will guide you to configure credentials properly.

---

## 🔄 Credential Rotation

Regularly update your GİB credentials:

1. **Change your GİB password** on the portal
2. **Update `.env` file** with new password
3. **Restart the MCP server**
4. **Test the connection**

```bash
# After updating .env
# Restart Claude Desktop to reload credentials
```

---

## 🕵️ What to Do If Credentials Are Exposed

If you accidentally commit credentials to Git:

### 1. **Immediately Change Your Password**
   - Login to GİB portal
   - Change your password immediately
   - Update `.env` with new password

### 2. **Remove from Git History**

```bash
# Remove file from Git history (use with caution!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (only if you own the repo)
git push origin --force --all
```

### 3. **Notify Relevant Parties**
   - If it's a company account, notify your IT security team
   - If pushed to public GitHub, assume credentials are compromised

### 4. **Review Access Logs**
   - Check GİB portal for unauthorized access
   - Review invoice activity

---

## 📝 Code Review Guidelines

When reviewing code:

- ✅ Check that `.env` is in `.gitignore`
- ✅ Verify no hardcoded credentials in code
- ✅ Ensure credentials are loaded from environment
- ✅ Confirm error messages don't leak credentials
- ✅ Check that credentials aren't logged

---

## 🔗 Additional Resources

- [GİB e-Fatura Portal](https://efatura.gib.gov.tr/)
- [GİB Test Portal](https://test.efatura.gov.tr/efatura/)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

---

## 📧 Security Contact

If you discover a security vulnerability in this MCP server:

1. **DO NOT** open a public GitHub issue
2. Contact the repository maintainer directly
3. Provide details of the vulnerability
4. Allow time for a fix before public disclosure

---

## ⚖️ Disclaimer

This MCP server is provided as-is. Users are responsible for:
- Securing their own credentials
- Complying with GİB terms of service
- Following Turkish tax and data protection laws
- Implementing additional security measures as needed

**Use at your own risk. The authors are not responsible for credential exposure or unauthorized access.**

---

**Last Updated:** December 5, 2024
