# huv - Hierarchical UV Virtual Environment Manager

A powerful wrapper around [uv](https://github.com/astral-sh/uv) that creates hierarchical virtual environments where child environments can inherit packages from parent environments with proper precedence handling.

## ✨ Features

- 🏗️ **Hierarchical Virtual Environments**: Create child environments that inherit from parent environments
- 📦 **Smart Package Management**: Automatically skip installing packages that are already available from parent environments
- 🔍 **Dependency Analysis**: Full dependency tree analysis to avoid duplicate installations
- ⚡ **Storage Efficient**: Minimize disk usage by sharing common packages across environments
- 🎯 **Version Conflict Detection**: Detect and handle version conflicts between parent and child environments
- 🛠️ **Complete uv Compatibility**: Full support for all uv venv and pip install flags and options
- 🔧 **Seamless Integration**: Drop-in replacement for uv with added hierarchical capabilities

## 📋 Requirements

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) installed and available in PATH

Install uv if you haven't already:

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Windows (via winget):**
```cmd
winget install astral-sh.uv
```

## 🚀 Installation

### Option 1: Install via pip (Recommended)
```bash
pip install huv
```

### Option 2: Run standalone executable
```bash
# Download the standalone executable
curl -LsSf https://github.com/your-org/huv/releases/latest/download/huv -o huv
chmod +x huv

# Move to a directory in your PATH (optional)
mv huv /usr/local/bin/
```

### Option 3: Install from source
```bash
git clone https://github.com/your-org/huv.git
cd huv
pip install .
```

## 📖 Quick Start

### Create a Root Environment
```bash
# Create a root environment with common packages
huv venv .vroot
```

**Activating on Linux/macOS:**
```bash
cd .vroot && source bin/activate
uv pip install numpy pandas requests
deactivate && cd ..
```

**Activating on Windows:**
```cmd
cd .vroot && Scripts\activate.bat
uv pip install numpy pandas requests
deactivate && cd ..
```

### Create Child Environments
```bash
# Create a child environment that inherits from .vroot
huv venv .vchild --parent .vroot
```

**Activating on Linux/macOS:**
```bash
cd .vchild && source bin/activate

# numpy, pandas, requests are already available from parent!
python -c "import numpy, pandas, requests; print('All packages available!')"
```

**Activating on Windows:**
```cmd
cd .vchild && Scripts\activate.bat

# numpy, pandas, requests are already available from parent!
python -c "import numpy, pandas, requests; print('All packages available!')"
```

### Smart Package Installation
```bash
# Install matplotlib - huv will skip numpy (available from parent)
huv pip install matplotlib

# Output:
# 🔍 Analyzing dependencies...
# 📋 Found 11 total packages (including dependencies)
# 📦 Dependency 'numpy' (v2.3.3 available from parent)
# 📦 Dependency 'packaging' (v25.0 available from parent)
# 📥 Installing 8 package(s)
# ⏭️  Skipped 3 package(s) available from parent
```

## 🔧 Commands

### Environment Creation
```bash
# Create a standalone environment
huv venv myenv

# Create a hierarchical environment
huv venv child-env --parent parent-env

# Pass through uv options
huv venv myenv --python 3.11 --seed
```

### Virtual Environment Options

huv supports all uv venv parameters while adding hierarchical functionality:

#### Core Environment Options
```bash
# Initialize with seed packages (pip, setuptools, wheel)
huv venv myenv --seed

# Clear existing environment if it exists
huv venv myenv --clear

# Custom prompt name
huv venv myenv --prompt "MyProject"

# Include system site packages
huv venv myenv --system-site-packages
```

#### Python Version Control
```bash
# Specify Python version
huv venv myenv --python 3.11
huv venv myenv -p python3.12

# Use managed Python installations
huv venv myenv --managed-python 3.11
```

#### Package Index Configuration
```bash
# Custom package index
huv venv myenv --index https://custom-index.com/simple/

# Default index configuration
huv venv myenv --default-index

# Find links for packages
huv venv myenv --find-links https://download.pytorch.org/whl/
huv venv myenv -f ./local-packages/
```

#### Performance and Caching Options
```bash
# Control file linking behavior
huv venv myenv --link-mode copy      # Copy files instead of hard links
huv venv myenv --link-mode hardlink  # Use hard links (default)
huv venv myenv --link-mode symlink   # Use symbolic links

# Cache management
huv venv myenv --cache-dir /custom/cache/path
huv venv myenv --refresh             # Refresh package metadata

# Combined hierarchical and performance options
huv venv child --parent .base --seed --python 3.11 --link-mode copy
```

### Package Management
```bash
# Smart install (skips packages from parent)
huv pip install package1 package2

# Install from requirements files
huv pip install -r requirements.txt

# Editable installs
huv pip install -e ./my-package

# Install with constraints
huv pip install -c constraints.txt package1

# Install with extras
huv pip install package[extra1,extra2]
huv pip install --extra security requests

# Upgrade packages
huv pip install -U package1

# Custom indexes
huv pip install --index-url https://custom-index.com package1
huv pip install --extra-index-url https://extra-index.com package1

# Advanced options
huv pip install --no-deps package1      # Skip dependencies
huv pip install --user package1         # User install
huv pip install --target ./lib package1 # Target directory

# Uninstall with parent visibility
huv pip uninstall package1
```

## 🎯 Use Cases

### Development Environments
**Linux/macOS:**
```bash
# Base environment with common tools
huv venv .base
source .base/bin/activate && uv pip install pytest black ruff mypy

# Project-specific environments
huv venv project1 --parent .base  # Inherits pytest, black, etc.
huv venv project2 --parent .base  # Inherits pytest, black, etc.
```

**Windows:**
```cmd
# Base environment with common tools
huv venv .base
.base\Scripts\activate.bat && uv pip install pytest black ruff mypy

# Project-specific environments
huv venv project1 --parent .base  # Inherits pytest, black, etc.
huv venv project2 --parent .base  # Inherits pytest, black, etc.
```

### Machine Learning Workflows
**Linux/macOS:**
```bash
# Base ML environment
huv venv .ml-base
source .ml-base/bin/activate && uv pip install numpy pandas scikit-learn

# Experiment environments
huv venv experiment1 --parent .ml-base  # + tensorflow
huv venv experiment2 --parent .ml-base  # + pytorch
```

**Windows:**
```cmd
# Base ML environment
huv venv .ml-base
.ml-base\Scripts\activate.bat && uv pip install numpy pandas scikit-learn

# Experiment environments
huv venv experiment1 --parent .ml-base  # + tensorflow
huv venv experiment2 --parent .ml-base  # + pytorch
```

### Microservices
**Linux/macOS:**
```bash
# Shared utilities environment
huv venv .shared
source .shared/bin/activate && uv pip install requests pydantic fastapi

# Service-specific environments
huv venv auth-service --parent .shared     # + additional auth packages
huv venv user-service --parent .shared     # + additional user packages
```

**Windows:**
```cmd
# Shared utilities environment
huv venv .shared
.shared\Scripts\activate.bat && uv pip install requests pydantic fastapi

# Service-specific environments
huv venv auth-service --parent .shared     # + additional auth packages
huv venv user-service --parent .shared     # + additional user packages
```

## 🏗️ How It Works

1. **Environment Creation**: `huv venv` creates a standard uv virtual environment with full support for all uv venv parameters, then modifies the activation scripts to include parent environment paths in `PYTHONPATH`

2. **Package Resolution**: `huv pip install` analyzes the complete dependency tree and checks which packages are already available from parent environments

3. **Smart Installation**: Only packages not available from parents are installed, using `--no-deps` when necessary to avoid conflicts

4. **Precedence**: Child environment packages always take precedence over parent packages

## 🖥️ Cross-Platform Support

huv works seamlessly across Linux, macOS, and Windows with automatic OS detection and platform-specific handling:

### Platform Differences
- **Linux/macOS**: Uses `bin/activate` scripts and `lib/python*/site-packages` directories
- **Windows**: Uses `Scripts\activate.bat` scripts and `Lib\site-packages` directories

### Activation Commands
**Linux/macOS:**
```bash
source myenv/bin/activate
```

**Windows Command Prompt:**
```cmd
myenv\Scripts\activate.bat
```

**Windows PowerShell:**
```powershell
myenv\Scripts\Activate.ps1
```

### Environment Structure
**Linux/macOS:**
```
myenv/
├── bin/
│   ├── activate
│   ├── activate.fish
│   ├── activate.csh
│   ├── activate.nu
│   └── python
├── lib/
│   └── python3.x/
│       └── site-packages/
└── pyvenv.cfg
```

**Windows:**
```
myenv\
├── Scripts\
│   ├── activate.bat
│   ├── Activate.ps1
│   └── python.exe
├── Lib\
│   └── site-packages\
└── pyvenv.cfg
```

All huv features work identically across platforms - only the activation commands differ.

## 📚 Complete Flag Support

huv provides comprehensive support for both uv venv and uv pip install commands while maintaining hierarchical functionality.

### Requirements and Constraints
```bash
# Requirements files (with comments and empty lines supported)
huv pip install -r requirements.txt -r dev-requirements.txt

# Constraint files  
huv pip install -c constraints.txt package1

# Editable installs
huv pip install -e ./my-package -e git+https://github.com/user/repo.git
```

### Package Sources and Indexes
```bash
# Custom package indexes
huv pip install -i https://custom-index.com/simple/ package1
huv pip install --extra-index-url https://extra-index.com/simple/ package1

# Find links (local or remote archives)
huv pip install -f https://example.com/packages/ package1
huv pip install -f ./local-packages/ package1

# Ignore PyPI entirely
huv pip install --no-index -f ./local-packages/ package1
```

### Package Extras and Dependencies
```bash
# Install with extras
huv pip install --extra security --extra testing requests
huv pip install --all-extras package1

# Control dependency installation
huv pip install --no-deps package1  # Skip dependencies entirely
```

### Upgrade and Reinstall Options
```bash
# Upgrade packages
huv pip install -U package1         # Upgrade specific package
huv pip install -P package1 -P package2  # Upgrade specific packages

# Force reinstallation
huv pip install --force-reinstall package1
```

### Installation Targets
```bash
# User installation
huv pip install --user package1

# Custom target directory
huv pip install --target ./mylib package1

# Custom prefix
huv pip install --prefix /opt/myapp package1
```

### Build Control
```bash
# Control wheel/source usage
huv pip install --no-binary package1    # Force source build
huv pip install --only-binary package1  # Only use wheels
huv pip install --no-build package1     # Don't build sources

# Security requirements
huv pip install --require-hashes -r requirements.txt
```

## 🔧 Environment Management

### Python Version Consistency

huv automatically ensures Python version consistency in hierarchical environments:

```bash
# Create parent with Python 3.11
huv venv .parent --python 3.11

# Child automatically inherits Python 3.11
huv venv child --parent .parent  # Uses Python 3.11 automatically

# Error if trying to use different version
huv venv child --parent .parent --python 3.10  # ❌ Error: Version mismatch
```

### Environment Information

**Check environment hierarchy:**
```bash
cat child/pyvenv.cfg | grep huv_parent
# Output: huv_parent = /path/to/.parent
```

**Verify package inheritance:**

**Linux/macOS:**
```bash
source child/bin/activate
python -c "import sys; print(sys.path)"  # Shows parent paths
```

**Windows:**
```cmd
child\Scripts\activate.bat
python -c "import sys; print(sys.path)"  # Shows parent paths
```

### Cleanup and Management

```bash
# Remove environments (children first)
rm -rf child/
rm -rf .parent/

# Check what packages come from where
huv pip list  # Shows local packages only
pip list      # Shows all packages (including inherited)
```

## 🛠️ Advanced Usage

### Advanced Installation Options

#### Version Constraints
```bash
# huv respects version constraints
huv pip install "numpy>=1.20"  # Skips if parent has compatible version
huv pip install "numpy>=2.0"   # Installs if parent has numpy 1.x
```

#### Multiple Requirements Sources
```bash
# Combine requirements files, constraints, and packages
huv pip install -r requirements.txt -c constraints.txt package1 package2

# Install with multiple requirement files
huv pip install -r base-requirements.txt -r dev-requirements.txt

# Mix editable and regular packages
huv pip install -e ./my-lib package1 package2
```

#### Build and Installation Control
```bash
# Control build process
huv pip install --no-build package1        # Don't build from source
huv pip install --no-binary :all: package1 # Force source builds
huv pip install --only-binary :all: package1 # Only use wheels

# Reinstall packages
huv pip install --force-reinstall package1

# Security options
huv pip install --require-hashes -r locked-requirements.txt
```

### Multiple Inheritance Levels
```bash
huv venv .base
huv venv .ml --parent .base
huv venv .deep-learning --parent .ml  # Inherits from both .ml and .base
```

### Advanced Environment Configuration
```bash
# Create optimized hierarchical environments
huv venv .base --seed --python 3.11 --link-mode hardlink
huv venv project1 --parent .base --prompt "Project1" --clear

# Development environment with custom index
huv venv dev --parent .base --index https://test.pypi.org/simple/ --seed

# Performance-optimized environment
huv venv fast-env --parent .base --link-mode copy --cache-dir ./local-cache
```

### Development Workflow
```bash
# Create development environment structure
huv venv .deps                           # Common dependencies
huv venv .tools --parent .deps           # + development tools  
huv venv myproject --parent .tools       # + project-specific packages
```

## 🐛 Troubleshooting

### Common Issues

#### Environment Creation Fails
```bash
# Error: Path already exists
rm -rf existing-path && huv venv existing-path

# Error: Parent environment not found
huv venv child --parent /path/to/missing  # Check parent path
```

#### Package Installation Issues
```bash
# Force installation if dependency analysis fails
huv pip install --no-deps package-name

# Clear cache if having dependency resolution issues
uv cache clean

# Check what packages are inherited
```

**Linux/macOS:**
```bash
source child/bin/activate
python -c "import package; print(package.__file__)"  # Shows source location
```

**Windows:**
```cmd
child\Scripts\activate.bat
python -c "import package; print(package.__file__)"  # Shows source location
```

#### Python Version Issues
**Linux/macOS:**
```bash
# Check parent Python version
parent-env/bin/python --version

# Create child with explicit version matching parent
huv venv child --parent parent-env --python 3.11
```

**Windows:**
```cmd
# Check parent Python version
parent-env\Scripts\python.exe --version

# Create child with explicit version matching parent
huv venv child --parent parent-env --python 3.11
```

### Performance Tips

- Use `--link-mode hardlink` for fastest environment creation
- Share a base environment across multiple projects to save disk space
- Use `--no-deps` for packages when you know dependencies are satisfied by parents
- Keep environment hierarchies shallow (2-3 levels max) for best performance

### Debugging

```bash
# Enable verbose output for uv operations
export UV_VERBOSE=1
huv pip install package-name

# Check inheritance chain
huv venv child --parent .parent --verbose  # If supported

# Manual inspection of environment
cat child/pyvenv.cfg
```

**Check activation script modifications:**

**Linux/macOS:**
```bash
cat child/bin/activate  # Check PYTHONPATH modifications
```

**Windows:**
```cmd
type child\Scripts\activate.bat  # Check PYTHONPATH modifications
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Project Structure

huv is designed as a single standalone executable for maximum portability:

```
huv                    # Main executable (Python script)
├── README.md         # Documentation
├── LICENSE           # MIT License
└── pyproject.toml    # Build configuration
```

The `huv` file contains the complete application and can be run directly without installation. This design makes it easy to:
- Distribute as a single file
- Run without complex dependencies
- Integrate into existing workflows
- Deploy in containerized environments

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/your-org/huv.git
cd huv

# Run tests
./run_tests.sh

# Or run specific tests
python tests/test_huv.py

# Test manually
./huv venv test-env
./huv venv test-child --parent test-env
```

### Running Tests

The project includes comprehensive tests:

```bash
# Run all tests (unit + integration)
./run_tests.sh

# Run only unit tests
python tests/test_huv.py

# Run with Python's unittest
python -m unittest tests.test_huv

# Run specific test
python tests/test_huv.py TestHuv.test_create_hierarchical_venv
```

### Code Quality

The project maintains high code quality standards:

- Comprehensive test coverage (15+ test cases)
- GitHub Actions CI/CD for multi-platform testing
- Support for Python 3.8+ across Linux, macOS, and Windows
- Automated testing on every commit

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on top of the excellent [uv](https://github.com/astral-sh/uv) package manager
- Inspired by the need for more efficient virtual environment management
- Thanks to the Python packaging community for the tools and standards
