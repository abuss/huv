# huv - Hierarchical UV Virtual Environment Manager

A powerful wrapper around [uv](https://github.com/astral-sh/uv) that creates hierarchical virtual environments where child environments can inherit packages from parent environments with proper precedence handling.

## ✨ Features

- 🏗️ **Hierarchical Virtual Environments**: Create child environments that inherit from parent environments
- 📦 **Smart Package Management**: Automatically skip installing packages that are already available from parent environments
- 🔍 **Dependency Analysis**: Full dependency tree analysis to avoid duplicate installations
- ⚡ **Storage Efficient**: Minimize disk usage by sharing common packages across environments
- 🎯 **Version Conflict Detection**: Detect and handle version conflicts between parent and child environments
- 🛠️ **uv Compatible**: Full compatibility with existing uv commands and workflows

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

### Package Management
```bash
# Smart install (skips packages from parent)
huv pip install package1 package2

# Uninstall with parent visibility
huv pip uninstall package1

# All uv pip options are supported
huv pip install "package>=1.0" --index-url https://custom-index.com
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

1. **Environment Creation**: `huv venv` creates a standard uv virtual environment and modifies the activation scripts to include parent environment paths in `PYTHONPATH`

2. **Package Resolution**: `huv pip install` analyzes the complete dependency tree and checks which packages are already available from parent environments

3. **Smart Installation**: Only packages not available from parents are installed, using `--no-deps` when necessary to avoid conflicts

4. **Precedence**: Child environment packages always take precedence over parent packages

## 🛠️ Advanced Usage

### Version Constraints
```bash
# huv respects version constraints
huv pip install "numpy>=1.20"  # Skips if parent has compatible version
huv pip install "numpy>=2.0"   # Installs if parent has numpy 1.x
```

### Multiple Inheritance Levels
```bash
huv venv .base
huv venv .ml --parent .base
huv venv .deep-learning --parent .ml  # Inherits from both .ml and .base
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