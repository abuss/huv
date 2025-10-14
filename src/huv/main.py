#!/usr/bin/env python3
"""
huv - Hierarchical UV Virtual Environment Manager

A wrapper around uv to create hierarchical virtual environments where child environments
can inherit packages from parent environments with proper precedence handling.

Features:
- Create hierarchical virtual environments with automatic inheritance
- Smart pip install that skips packages available from parent environments
- pip uninstall with visibility into what remains available from parents
- Full compatibility with uv and standard virtual environments

Usage:
    huv venv <path> [--parent <parent_path>] [other uv options]
    huv pip install <packages...>
    huv pip uninstall <packages...>
    huv --help
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


class HierarchicalUV:
    def __init__(self):
        self.uv_executable = self._find_uv()
        self.current_venv = self._get_current_venv()

    def _find_uv(self):
        """Find the uv executable in PATH"""
        import shutil

        uv_path = shutil.which("uv")
        if not uv_path:
            print(
                "Error: 'uv' not found in PATH. Please install uv first.",
                file=sys.stderr,
            )
            print(
                "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh",
                file=sys.stderr,
            )
            sys.exit(1)
        return uv_path

    def create_venv(self, venv_path, parent_path=None, uv_args=None):
        """Create a virtual environment with optional parent hierarchy"""
        venv_path = Path(venv_path).resolve()

        # Check if target already exists
        if venv_path.exists():
            if (venv_path / "pyvenv.cfg").exists():
                print(
                    f"Error: Virtual environment already exists at '{venv_path}'",
                    file=sys.stderr,
                )
                sys.exit(1)
            elif any(venv_path.iterdir()):
                print(
                    f"Error: Directory '{venv_path}' exists and is not empty",
                    file=sys.stderr,
                )
                sys.exit(1)

        # Validate parent environment if specified
        if parent_path:
            parent_path = Path(parent_path).resolve()
            if not parent_path.exists():
                print(
                    f"Error: Parent environment '{parent_path}' does not exist.",
                    file=sys.stderr,
                )
                sys.exit(1)
            if not (parent_path / "pyvenv.cfg").exists():
                print(
                    f"Error: '{parent_path}' is not a valid virtual environment.",
                    file=sys.stderr,
                )
                sys.exit(1)
            if not (parent_path / "bin" / "activate").exists():
                print(
                    f"Error: Parent environment '{parent_path}' is missing activate script.",
                    file=sys.stderr,
                )
                sys.exit(1)

        # Build uv command
        cmd = [self.uv_executable, "venv", str(venv_path)]
        if uv_args:
            cmd.extend(uv_args)

        print(f"Creating virtual environment: {venv_path}")
        if parent_path:
            print(f"Parent environment: {parent_path}")

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}", file=sys.stderr)
            sys.exit(1)

        # Verify the environment was created successfully
        if not (venv_path / "bin" / "activate").exists():
            print(
                "Error: Virtual environment creation failed - missing activate script",
                file=sys.stderr,
            )
            sys.exit(1)

        # If parent is specified, modify activation scripts
        if parent_path:
            print(f"Setting up hierarchy with parent: {parent_path}")
            try:
                self._setup_hierarchy(venv_path, parent_path)
            except Exception as e:
                print(f"Error setting up hierarchy: {e}", file=sys.stderr)
                print(
                    "Virtual environment created but hierarchy setup failed.",
                    file=sys.stderr,
                )
                sys.exit(1)

        print(f"✓ Virtual environment created successfully at: {venv_path}")
        if parent_path:
            print(f"✓ Hierarchy configured with parent: {parent_path}")
            print(f"  Use: source {venv_path}/bin/activate")

    def _setup_hierarchy(self, venv_path, parent_path):
        """Modify activation scripts to support hierarchy"""
        self._modify_bash_activate(venv_path, parent_path)
        self._modify_activate_this_py(venv_path, parent_path)

    def _modify_bash_activate(self, venv_path, parent_path):
        """Modify the bash activate script"""
        activate_script = venv_path / "bin" / "activate"

        if not activate_script.exists():
            print(f"Warning: Activate script not found at {activate_script}")
            return

        # Read the original script
        with open(activate_script) as f:
            content = f.read()

        # Find the deactivate function and add PYTHONPATH restoration
        deactivate_insertion = """    if ! [ -z "${_OLD_VIRTUAL_PYTHONHOME+_}" ] ; then
        PYTHONHOME="$_OLD_VIRTUAL_PYTHONHOME"
        export PYTHONHOME
        unset _OLD_VIRTUAL_PYTHONHOME
    fi
    if ! [ -z "${_OLD_VIRTUAL_PYTHONPATH+_}" ] ; then
        PYTHONPATH="$_OLD_VIRTUAL_PYTHONPATH"
        export PYTHONPATH
        unset _OLD_VIRTUAL_PYTHONPATH
    elif [ ! -z "${PYTHONPATH+_}" ] ; then
        unset PYTHONPATH
    fi"""

        # Replace the PYTHONHOME section in deactivate function
        old_pythonhome_section = """    if ! [ -z "${_OLD_VIRTUAL_PYTHONHOME+_}" ] ; then
        PYTHONHOME="$_OLD_VIRTUAL_PYTHONHOME"
        export PYTHONHOME
        unset _OLD_VIRTUAL_PYTHONHOME
    fi"""

        content = content.replace(old_pythonhome_section, deactivate_insertion)

        # Add hierarchical support at the end
        hierarchy_code = f'''
# Hierarchical environment support - include parent libraries
PARENT_VENV_PATH="{parent_path}"
if [ -d "$PARENT_VENV_PATH" ]; then
    # Store old PYTHONPATH
    if ! [ -z "${{PYTHONPATH+_}}" ] ; then
        _OLD_VIRTUAL_PYTHONPATH="$PYTHONPATH"
    fi
    
    # Add parent site-packages to PYTHONPATH (appended, so child takes precedence)
    # Use find to locate site-packages directories to avoid shell glob issues
    for parent_site in "$PARENT_VENV_PATH"/lib/python*/site-packages; do
        if [ -d "$parent_site" ]; then
            if [ -z "${{PYTHONPATH+_}}" ]; then
                PYTHONPATH="$parent_site"
            else
                PYTHONPATH="$PYTHONPATH:$parent_site"
            fi
        fi
    done
    if [ ! -z "${{PYTHONPATH+_}}" ]; then
        export PYTHONPATH
    fi
fi

'''

        # Insert before the final hash command
        hash_line = "hash -r 2>/dev/null || true"
        content = content.replace(hash_line, hierarchy_code + hash_line)

        # Write the modified script
        with open(activate_script, "w") as f:
            f.write(content)

    def _modify_activate_this_py(self, venv_path, parent_path):
        """Modify the activate_this.py script"""
        activate_this = venv_path / "bin" / "activate_this.py"

        if not activate_this.exists():
            print(f"Warning: activate_this.py not found at {activate_this}")
            return

        # Read the original script
        with open(activate_this) as f:
            content = f.read()

        # Detect Python version from the existing script
        import re

        version_match = re.search(r"python(\d+\.\d+)", content)
        python_version = version_match.group(1) if version_match else "3.*"

        # Find the sys.path modification section (more flexible matching)
        old_pattern = (
            r"# add the virtual environments libraries.*?sys\.path\[:] = .*?\n"
        )

        # Create the new hierarchical version
        new_syspath_section = f'''# add the virtual environments libraries to the host python import mechanism
import glob
prev_length = len(sys.path)

# Add child environment libraries first (highest precedence)
child_lib_pattern = os.path.join(bin_dir, "..", "lib", "python*", "site-packages")
for child_site_packages in glob.glob(child_lib_pattern):
    if os.path.exists(child_site_packages):
        site.addsitedir(child_site_packages)

# Add parent environment libraries (lower precedence)
parent_venv_path = "{parent_path}"
if os.path.exists(parent_venv_path):
    parent_lib_pattern = os.path.join(parent_venv_path, "lib", "python*", "site-packages")
    for parent_site_packages in glob.glob(parent_lib_pattern):
        if os.path.exists(parent_site_packages):
            site.addsitedir(parent_site_packages)

# Move new paths to front for proper precedence (child first, then parent)
new_paths = sys.path[prev_length:]
sys.path[prev_length:] = []
sys.path[:0] = new_paths
'''

        # Replace the section using regex
        content = re.sub(old_pattern, new_syspath_section, content, flags=re.DOTALL)

        # Write the modified script
        with open(activate_this, "w") as f:
            f.write(content)

    def _get_current_venv(self):
        """Get the current virtual environment path"""
        venv_path = os.environ.get("VIRTUAL_ENV")
        if venv_path:
            return Path(venv_path)
        return None

    def _find_parent_venv(self, venv_path):
        """Find the parent virtual environment for a given venv"""
        if not venv_path:
            return None

        activate_script = venv_path / "bin" / "activate"
        if not activate_script.exists():
            return None

        try:
            with open(activate_script) as f:
                content = f.read()
                # Look for the PARENT_VENV_PATH line
                match = re.search(r'PARENT_VENV_PATH="([^"]*)"', content)
                if match:
                    parent_path = match.group(1)
                    if parent_path and Path(parent_path).exists():
                        return Path(parent_path)
        except Exception:
            pass
        return None

    def _get_installed_packages(self, venv_path):
        """Get installed packages in a virtual environment"""
        if not venv_path or not venv_path.exists():
            return {}

        python_exe = venv_path / "bin" / "python"
        if not python_exe.exists():
            return {}

        # Try uv pip first, then fall back to regular pip
        for pip_cmd in [
            [self.uv_executable, "pip", "list", "--format=json"],
            [str(python_exe), "-m", "pip", "list", "--format=json"],
        ]:
            try:
                # Set VIRTUAL_ENV for uv pip to work correctly
                env = os.environ.copy()
                env["VIRTUAL_ENV"] = str(venv_path)

                result = subprocess.run(
                    pip_cmd, capture_output=True, text=True, check=True, env=env
                )

                packages = {}
                for pkg in json.loads(result.stdout):
                    packages[pkg["name"].lower()] = pkg["version"]
                return packages
            except Exception:
                continue

        return {}

    def _get_parent_packages(self, venv_path):
        """Get all packages available from parent environments"""
        all_packages = {}
        current = venv_path

        while current:
            parent = self._find_parent_venv(current)
            if not parent:
                break

            parent_packages = self._get_installed_packages(parent)
            # Add packages that aren't already in our collection (child takes precedence)
            for pkg_name, version in parent_packages.items():
                if pkg_name not in all_packages:
                    all_packages[pkg_name] = version

            current = parent

        return all_packages

    def _get_dependency_tree(self, packages, pip_args=None):
        """Get the full dependency tree for packages using dry-run"""
        cmd = [self.uv_executable, "pip", "install", "--dry-run"] + packages
        if pip_args:
            cmd.extend(pip_args)

        try:
            # Temporarily remove PYTHONPATH to get accurate dependency analysis
            # This prevents uv from seeing parent packages as "already installed"
            env = os.environ.copy()
            old_pythonpath = env.pop("PYTHONPATH", None)

            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, env=env
            )

            # Parse the dry-run output to extract package names and versions
            dependencies = {}

            # uv output format: "Would install X packages" followed by " + package==version" lines
            lines = result.stdout.split("\n") + result.stderr.split("\n")

            for line in lines:
                line = line.strip()
                # Look for lines like " + package==version"
                if line.startswith("+") and "==" in line:
                    pkg_info = line[1:].strip()  # Remove "+"
                    if "==" in pkg_info:
                        pkg_name, version = pkg_info.split("==", 1)
                        dependencies[pkg_name.lower()] = version

            return dependencies
        except subprocess.CalledProcessError:
            # If dry-run fails, fall back to the original approach
            return {}

    def _parse_version_constraint(self, pkg_spec):
        """Parse package specification to extract name and version constraint"""
        # Handle specifications like "numpy>=1.0", "requests==2.0", etc.
        match = re.match(r"^([a-zA-Z0-9_.-]+)(.*)$", pkg_spec.strip())
        if match:
            pkg_name = match.group(1)
            constraint = match.group(2) if match.group(2) else ""
            return pkg_name.lower(), constraint
        return pkg_spec.lower(), ""

    def _is_version_compatible(self, available_version, constraint):
        """Check if available version satisfies the constraint"""
        if not constraint:
            return True

        # Simple version comparison - for a full solution, we'd use packaging.specifiers
        # This handles the most common cases
        if constraint.startswith(">="):
            required = constraint[2:].strip()
            return available_version >= required
        elif constraint.startswith("=="):
            required = constraint[2:].strip()
            return available_version == required
        elif constraint.startswith(">"):
            required = constraint[1:].strip()
            return available_version > required
        elif constraint.startswith("<="):
            required = constraint[2:].strip()
            return available_version <= required
        elif constraint.startswith("<"):
            required = constraint[1:].strip()
            return available_version < required

        # Default to compatible for complex constraints
        return True

    def pip_install(self, packages, pip_args=None):
        """Install packages with parent dependency checking"""
        if not self.current_venv:
            print(
                "Error: No active virtual environment. Please activate one first.",
                file=sys.stderr,
            )
            sys.exit(1)

        if not packages:
            print("Error: No packages specified for installation.", file=sys.stderr)
            sys.exit(1)

        # Get packages available from parents
        parent_packages = self._get_parent_packages(self.current_venv)

        print("🔍 Analyzing dependencies...")

        # Get full dependency tree using dry-run
        dependency_tree = self._get_dependency_tree(packages, pip_args)

        if dependency_tree:
            print(
                f"📋 Found {len(dependency_tree)} total packages (including dependencies)"
            )

            # Check each package in the dependency tree
            packages_to_install = []
            skipped_packages = []
            version_conflicts = []

            # First, handle the explicitly requested packages
            explicit_packages = set()
            for pkg_spec in packages:
                pkg_name, constraint = self._parse_version_constraint(pkg_spec)
                explicit_packages.add(pkg_name)

                if pkg_name in parent_packages:
                    available_version = parent_packages[pkg_name]
                    if self._is_version_compatible(available_version, constraint):
                        print(
                            f"📦 Skipping '{pkg_name}' (v{available_version} from parent satisfies {constraint or 'any version'})"
                        )
                        skipped_packages.append(pkg_name)
                    else:
                        print(
                            f"⚠️  Parent has '{pkg_name}' v{available_version}, but need {constraint}"
                        )
                        packages_to_install.append(pkg_spec)
                        version_conflicts.append(
                            f"{pkg_name}: parent v{available_version} vs required {constraint}"
                        )
                else:
                    packages_to_install.append(pkg_spec)

            # Then handle dependencies
            for dep_name, dep_version in dependency_tree.items():
                if dep_name in explicit_packages:
                    continue  # Already handled above

                if dep_name in parent_packages:
                    parent_version = parent_packages[dep_name]
                    print(
                        f"📦 Dependency '{dep_name}' (v{parent_version} available from parent)"
                    )
                    skipped_packages.append(dep_name)
                else:
                    # Add dependency to install list - we'll use --no-deps later
                    packages_to_install.append(dep_name)

            if version_conflicts:
                print("\n⚠️  Version conflicts detected:")
                for conflict in version_conflicts:
                    print(f"   {conflict}")
                print(
                    "   Child environment will override parent versions for these packages."
                )

        else:
            # Fallback to original logic if dry-run fails
            print("⚠️  Could not analyze dependencies, using basic package checking")
            packages_to_install = []
            skipped_packages = []

            for pkg_spec in packages:
                pkg_name = re.split(r"[<>=!]", pkg_spec)[0].strip().lower()

                if pkg_name in parent_packages:
                    print(
                        f"📦 Skipping '{pkg_name}' (v{parent_packages[pkg_name]} available from parent)"
                    )
                    skipped_packages.append(pkg_name)
                else:
                    packages_to_install.append(pkg_spec)

        if not packages_to_install:
            print(
                "✅ All requested packages and dependencies are already available from parent environments."
            )
            return

        print(f"\n📥 Installing {len(packages_to_install)} package(s)")
        if skipped_packages:
            print(
                f"⏭️  Skipped {len(skipped_packages)} package(s) available from parent"
            )

        # Build uv pip install command
        # We need to be careful about dependencies - if we detected them, we might want --no-deps
        cmd = [self.uv_executable, "pip", "install"]

        if dependency_tree and skipped_packages:
            # If we skipped some dependencies, we need to install without automatic dependency resolution
            # to avoid conflicts with parent packages
            cmd.append("--no-deps")
            print("🔧 Using --no-deps to avoid conflicts with parent environment")

        cmd.extend(packages_to_install)
        if pip_args:
            cmd.extend(pip_args)

        # Run the installation
        try:
            subprocess.run(cmd, check=True)
            print("✅ Installation completed successfully.")

            if dependency_tree and skipped_packages:
                print("\n📦 Package hierarchy summary:")
                print(f"   • Installed in child: {len(packages_to_install)} packages")
                print(f"   • Available from parent: {len(skipped_packages)} packages")

        except subprocess.CalledProcessError as e:
            print(
                f"❌ Installation failed with exit code {e.returncode}", file=sys.stderr
            )
            sys.exit(e.returncode)

    def pip_uninstall(self, packages, pip_args=None):
        """Uninstall packages from current environment"""
        if not self.current_venv:
            print(
                "Error: No active virtual environment. Please activate one first.",
                file=sys.stderr,
            )
            sys.exit(1)

        if not packages:
            print("Error: No packages specified for uninstallation.", file=sys.stderr)
            sys.exit(1)

        # Get currently installed packages in this environment
        current_packages = self._get_installed_packages(self.current_venv)
        parent_packages = self._get_parent_packages(self.current_venv)

        packages_to_remove = []
        not_found = []
        parent_available = []

        for pkg_name in packages:
            pkg_name_lower = pkg_name.lower()

            if pkg_name_lower in current_packages:
                packages_to_remove.append(pkg_name)
                if pkg_name_lower in parent_packages:
                    parent_available.append(
                        f"{pkg_name} (v{parent_packages[pkg_name_lower]} still available from parent)"
                    )
            else:
                not_found.append(pkg_name)

        if not_found:
            print(
                f"⚠️  Packages not installed in current environment: {', '.join(not_found)}"
            )

        if not packages_to_remove:
            print("❌ No packages to uninstall from current environment.")
            return

        print(
            f"🗑️  Uninstalling {len(packages_to_remove)} package(s): {', '.join(packages_to_remove)}"
        )
        if parent_available:
            print(
                "📦 After uninstall, these packages will still be available from parent:"
            )
            for pkg in parent_available:
                print(f"   - {pkg}")

        # Build uv pip uninstall command
        cmd = [self.uv_executable, "pip", "uninstall"] + packages_to_remove
        if pip_args:
            cmd.extend(pip_args)

        # Run the uninstallation
        try:
            subprocess.run(cmd, check=True)
            print("✅ Uninstallation completed successfully.")
        except subprocess.CalledProcessError as e:
            print(
                f"❌ Uninstallation failed with exit code {e.returncode}",
                file=sys.stderr,
            )
            sys.exit(e.returncode)

    def passthrough_command(self, args):
        """Pass through commands directly to uv"""
        cmd = [self.uv_executable] + args

        try:
            # Use execvp to replace the current process with uv
            # This ensures that uv gets the exact same environment and signal handling
            os.execvp(self.uv_executable, cmd)
        except OSError as e:
            print(f"❌ Failed to execute uv: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    huv = HierarchicalUV()

    # Check if this is a huv-specific command that needs special handling
    if len(sys.argv) >= 2:
        if sys.argv[1] == "venv" and "--parent" in sys.argv:
            # Handle hierarchical venv creation
            parser = argparse.ArgumentParser(
                description="Create hierarchical virtual environment"
            )
            parser.add_argument("command")  # venv
            parser.add_argument("path", help="Path for the virtual environment")
            parser.add_argument("--parent", help="Parent virtual environment path")
            args, unknown_args = parser.parse_known_args()
            huv.create_venv(args.path, args.parent, unknown_args)
            return

        elif (
            sys.argv[1] == "pip"
            and len(sys.argv) >= 3
            and sys.argv[2] in ["install", "uninstall"]
        ):
            # Handle hierarchical pip commands
            if sys.argv[2] == "install":
                parser = argparse.ArgumentParser(
                    description="Install packages with hierarchy awareness"
                )
                parser.add_argument("command")  # pip
                parser.add_argument("subcommand")  # install
                parser.add_argument("packages", nargs="+", help="Packages to install")
                args, unknown_args = parser.parse_known_args()
                huv.pip_install(args.packages, unknown_args)
                return

            elif sys.argv[2] == "uninstall":
                parser = argparse.ArgumentParser(
                    description="Uninstall packages with hierarchy awareness"
                )
                parser.add_argument("command")  # pip
                parser.add_argument("subcommand")  # uninstall
                parser.add_argument("packages", nargs="+", help="Packages to uninstall")
                args, unknown_args = parser.parse_known_args()
                huv.pip_uninstall(args.packages, unknown_args)
                return

    # For all other commands, pass through to uv
    # Remove the script name and pass everything else
    if len(sys.argv) > 1:
        huv.passthrough_command(sys.argv[1:])
    else:
        # No arguments - show uv help
        huv.passthrough_command(["--help"])


if __name__ == "__main__":
    main()
