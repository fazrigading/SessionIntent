#!/bin/bash
# GJS Extension Lint Checker
# Usage: ./lint-gjs.sh extension.js

if [ -z "$1" ]; then
    echo "Usage: $0 <extension.js>"
    exit 1
fi

FILE="$1"
echo "=== GJS Extension Lint: $FILE ==="

ERRORS=0

# Check for known bad API calls
echo "Checking for known problematic API calls..."

# SocketService methods
if grep -qE "\.listen\(\)" "$FILE"; then
    echo "ERROR: .listen() does not exist on Gio.SocketService - use .start()"
    ERRORS=1
fi

if grep -qE "\.set_active\(" "$FILE"; then
    echo "ERROR: .set_active() does not exist on Gio.SocketService - use .start()/.stop()"
    ERRORS=1
fi

# connect() takes exactly 2 args
if grep -qE "\.connect\(.+,\s*[^,)]+\)\s*,\s*true\)" "$FILE"; then
    echo "ERROR: .connect() only takes 2 args - remove extra true"
    ERRORS=1
fi

# write_all_async takes 4 args, not 5
if grep -qE "\.write_all_async\([^)]+,\s*[^,)]+,\s*[^,)]+,\s*[^,)]+,\s*[^)]+\)" "$FILE"; then
    echo "ERROR: write_all_async() takes 4 args (buffer, count, priority, callback), not 5"
    ERRORS=1
fi

# write_async takes 4 args, not 5  
if grep -qE "\.write_async\([^)]+,\s*[^,)]+,\s*[^,)]+,\s*[^,)]+,\s*[^)]+\)" "$FILE"; then
    echo "ERROR: write_async() takes 4 args (buffer, count, priority, callback), not 5"
    ERRORS=1
fi

# read_async takes 3 args, not 4
if grep -qE "\.read_bytes_async\([^)]+,\s*[^,)]+,\s*[^,)]+,\s*[^,)]+,\s*[^)]+\)" "$FILE"; then
    echo "ERROR: read_bytes_async() takes 3 args (count, priority, cancellable, callback), not 4"
    ERRORS=1
fi

# is_active is property, not method
if grep -qE "\.is_active\(" "$FILE"; then
    echo "ERROR: is_active is a property, not a method - use .is_active (no parens)"
    ERRORS=1
fi

# Common typos
if grep -q "sessionintent-ws.sort" "$FILE"; then
    echo "ERROR: typo 'sessionintent-ws.sort' should be '.sock'"
    ERRORS=1
fi

echo ""
echo "=== API Reference ==="
echo "Gio.SocketService: .start(), .stop(), .is_active (property)"
echo "Gio.OutputStream.write_all_async: 4 args (buffer, count, priority, callback)"
echo "Gio.OutputStream.write_async: 4 args (buffer, count, priority, callback)"  
echo "Gio.InputStream.read_bytes_async: 4 args (count, priority, cancellable, callback)"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo "PASS - No issues found"
else
    echo "FAIL - Issues found"
fi

exit $ERRORS