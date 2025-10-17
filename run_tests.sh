#!/bin/bash
set -e

echo "Running huv test suite..."

# Change to script directory
cd "$(dirname "$0")"

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "Warning: uv not found in PATH. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Make huv executable
chmod +x huv

# Run basic functionality test
echo "Testing basic functionality..."
PYTHONPATH=. python -m tests.test_huv

# Run manual integration tests
echo "Running integration tests..."

# Clean up any existing test environments
rm -rf test-* 2>/dev/null || true

# Test standalone environment
echo "  - Testing standalone environment creation..."
./huv venv test-standalone
if [ ! -d "test-standalone" ]; then
    echo "ERROR: Standalone environment not created"
    exit 1
fi

# Test hierarchical environment
echo "  - Testing hierarchical environment creation..."
./huv venv test-parent
./huv venv test-child --parent test-parent

if [ ! -d "test-child" ]; then
    echo "ERROR: Child environment not created"
    exit 1
fi

# Check hierarchy setup in pyvenv.cfg and _virtualenv.py
if ! grep -q "huv_parent =" test-child/pyvenv.cfg; then
    echo "ERROR: Hierarchy not properly configured in pyvenv.cfg"
    exit 1
fi

# Find the _virtualenv.py file in the appropriate Python version directory
VIRTUALENV_PY_PATH=$(find test-child/lib -name "_virtualenv.py" -type f | head -1)
if [ -z "$VIRTUALENV_PY_PATH" ] || ! grep -q "_setup_huv_hierarchy" "$VIRTUALENV_PY_PATH"; then
    echo "ERROR: Hierarchy not properly set up in _virtualenv.py"
    exit 1
fi

# Test Python version inheritance
echo "  - Testing Python version inheritance..."
output=$(./huv venv test-inherit-child --parent test-parent 2>&1)
if ! echo "$output" | grep -q "Using parent's Python version"; then
    echo "ERROR: Python version inheritance not working"
    exit 1
fi

# Test with additional arguments
echo "  - Testing with additional uv arguments..."
./huv venv test-seed --seed
if [ ! -f "test-seed/bin/pip" ]; then
    echo "ERROR: Seed packages not installed"
    exit 1
fi

# Test error conditions
echo "  - Testing error conditions..."

# Test invalid parent
if ./huv venv test-invalid --parent nonexistent 2>/dev/null; then
    echo "ERROR: Should have failed with invalid parent"
    exit 1
fi

# Test existing directory
mkdir -p existing-dir
if ./huv venv existing-dir 2>/dev/null; then
    echo "ERROR: Should have failed with existing directory"
    exit 1
fi

# Clean up
rm -rf test-* existing-dir 2>/dev/null || true

echo "✅ All tests passed!"