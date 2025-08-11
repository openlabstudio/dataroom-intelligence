# Fixed Test Mode Check

# This is the corrected code block that should replace lines 226-232 in app.py
# The problem is that test_mode_check is only defined inside an if statement
# but then used outside of it, causing an undefined variable error

# CORRECT VERSION:
```python
        # Check for test mode - skip expensive AI analysis
        import os
        test_mode_value = os.getenv('TEST_MODE', 'false')
        test_mode_check = test_mode_value.lower() == 'true'
        logger.info(f"🔍 DEBUG - TEST_MODE check: {test_mode_check}")
        
        if test_mode_check:
            logger.info("🧪 TEST MODE: Skipping AI analysis, using mock session data")
            # Rest of the test mode code...
```

# INCORRECT VERSION (current):
```python
        # Check for test mode - skip expensive AI analysis
        import os
        if os.getenv('TEST_MODE', 'false').lower() == 'true':
            test_mode_check = os.getenv('TEST_MODE', 'false').lower() == 'true'
            logger.info(f"🔍 DEBUG - Second TEST_MODE check: {test_mode_check}")

        if test_mode_check:  # ERROR: test_mode_check not defined if condition above is false!
```

The fix is simple: define test_mode_check BEFORE the if statement, not inside it.
