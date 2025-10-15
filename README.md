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
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 🚀 Installation

```bash
pip install huv
```

## 📖 Quick Start

### Create a Root Environment
```bash
# Create a root environment with common packages
huv venv .vroot
cd .vroot && source bin/activate
uv pip install numpy pandas requests
deactivate && cd ..
```

### Create Child Environments
```bash
# Create a child environment that inherits from .vroot
huv venv .vchild --parent .vroot
cd .vchild && source bin/activate

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
```bash
# Base environment with common tools
huv venv .base
source .base/bin/activate && uv pip install pytest black ruff mypy

# Project-specific environments
huv venv project1 --parent .base  # Inherits pytest, black, etc.
huv venv project2 --parent .base  # Inherits pytest, black, etc.
```

### Machine Learning Workflows
```bash
# Base ML environment
huv venv .ml-base
source .ml-base/bin/activate && uv pip install numpy pandas scikit-learn

# Experiment environments
huv venv experiment1 --parent .ml-base  # + tensorflow
huv venv experiment2 --parent .ml-base  # + pytorch
```

### Microservices
```bash
# Shared utilities environment
huv venv .shared
source .shared/bin/activate && uv pip install requests pydantic fastapi

# Service-specific environments
huv venv auth-service --parent .shared     # + additional auth packages
huv venv user-service --parent .shared     # + additional user packages
```

## 🏗️ How It Works

1. **Environment Creation**: `huv venv` creates a standard uv virtual environment with full support for all uv venv parameters, then modifies the activation scripts to include parent environment paths in `PYTHONPATH`

2. **Package Resolution**: `huv pip install` analyzes the complete dependency tree and checks which packages are already available from parent environments

3. **Smart Installation**: Only packages not available from parents are installed, using `--no-deps` when necessary to avoid conflicts

4. **Precedence**: Child environment packages always take precedence over parent packages

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

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on top of the excellent [uv](https://github.com/astral-sh/uv) package manager
- Inspired by the need for more efficient virtual environment management
- Thanks to the Python packaging community for the tools and standards
