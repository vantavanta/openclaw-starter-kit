# Deployment Checklist

**Prevent the "deploy → assume working → breaks later" cycle.**

---

## The Pattern We're Preventing

**Common failure mode:**
1. Test locally → works ✅
2. Deploy to production → assume it works
3. Work on other things
4. Come back later → broken ❌
5. Debug the same issue again

**Fix:** Verify BEFORE and AFTER every deployment.

---

## Pre-Deployment Checklist

**BEFORE deploying ANY code:**

- [ ] Code tested locally (works on your machine)
- [ ] Dependencies installed/updated
- [ ] Configuration files reviewed (no hardcoded secrets)
- [ ] Run `gitleaks detect` (catch secrets before commit)
- [ ] Health check passes locally
- [ ] Backup current production version (can rollback)

**For critical systems (trading, automation, production):**
- [ ] Review with human (get approval for risky changes)
- [ ] Document what you're deploying and why
- [ ] Know the rollback procedure

---

## Deployment Steps

**Standard deployment:**

1. **Stop service** (if applicable)
   ```bash
   systemctl stop [service-name]
   # or kill process gracefully
   ```

2. **Backup current version**
   ```bash
   cp current_file.py current_file.py.backup-$(date +%Y%m%d-%H%M)
   ```

3. **Deploy new code**
   ```bash
   scp new_file.py production:/path/
   # or git pull, rsync, etc.
   ```

4. **Verify deployment**
   ```bash
   # Check file exists and has correct content
   ls -lh /path/new_file.py
   md5sum new_file.py  # Compare with local
   ```

5. **Start service**
   ```bash
   systemctl start [service-name]
   # or run process
   ```

---

## Post-Deployment Checklist

**IMMEDIATELY after deploying:**

- [ ] Service started successfully
- [ ] Process is running (check PID, not just "active")
- [ ] **Run health check** (verify core functionality)
- [ ] Check logs for errors (first 60 seconds)
- [ ] Verify it's doing what it should (API calls, data processing, etc.)

**For trading/financial systems:**
- [ ] Balance check works
- [ ] Can fetch market data
- [ ] Can place test order (or verify order placement works)
- [ ] Position tracking accurate

**For data systems:**
- [ ] APIs responding
- [ ] Data being collected
- [ ] Storage working (files being written)

---

## Health Check Template

**Create a `health_check` script for each system:**

```python
#!/usr/bin/env python3
"""
System Health Check - Run before and after deployment
"""

def check_api_connection():
    """Verify API is reachable"""
    # Test API call
    pass

def check_authentication():
    """Verify credentials work"""
    # Test authenticated call
    pass

def check_core_functionality():
    """Verify main function works"""
    # Test primary operation
    pass

def check_data_access():
    """Verify can read/write data"""
    # Test database, files, etc.
    pass

if __name__ == '__main__':
    print("🏥 Running health check...")
    
    tests = [
        ("API Connection", check_api_connection),
        ("Authentication", check_authentication),
        ("Core Functionality", check_core_functionality),
        ("Data Access", check_data_access),
    ]
    
    passed = 0
    for name, test in tests:
        try:
            test()
            print(f"✅ {name}")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    print(f"\n{passed}/{len(tests)} checks passed")
    
    if passed < len(tests):
        exit(1)  # Fail if any check failed
```

**Run this:**
- Before deployment (verify current system works)
- After deployment (verify new system works)
- On schedule (detect drift/degradation)

---

## Rollback Procedure

**If post-deployment health check fails:**

1. **Don't optimize, don't debug - ROLLBACK FIRST**
   ```bash
   systemctl stop [service]
   cp current_file.py.backup-[timestamp] current_file.py
   systemctl start [service]
   ```

2. **Verify rollback worked**
   ```bash
   ./health_check.sh
   ```

3. **THEN debug offline**
   - Don't fix in production
   - Replicate locally
   - Fix and test
   - Deploy again (following checklist)

---

## Maintenance Deployments

**For updates that don't change functionality:**

Still run health checks. You'd be surprised how often "minor updates" break things.

**Examples:**
- Dependency upgrades
- Configuration changes
- Performance optimizations
- Logging improvements

**Same checklist applies.**

---

## Document the Deployment

**After successful deployment:**

Create a brief deployment log:
```markdown
## Deployment - 2026-02-18 15:30

**What:** Storm Chaser V6.1 - WebSocket indexing fix
**Why:** Orderbooks weren't populating, causing manual override dependency
**Changes:**
- Updated websocket_orderbook.py with local indexing
- Added REST API fallback for cannon loading
- Fixed PING/PONG message handling

**Health check:**
- Pre: ✅ OMS responding, balance $49.23
- Post: ✅ OMS responding, balance $49.23, orderbooks populating

**Rollback plan:** Backup at ~/vanta/strategies/.../v6.0.backup

**Status:** ✅ Deployed successfully, monitoring
```

---

## Summary

**Three rules:**
1. Health check BEFORE deployment (know current state works)
2. Deploy
3. Health check AFTER deployment (verify new state works)

**If step 3 fails → rollback immediately, debug offline.**

**This prevents recurring breakage.**

The 5 minutes spent on health checks saves hours of debugging.
