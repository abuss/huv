#!/usr/bin/env python3
"""
Comprehensive test suite for huv (Hierarchical UV) functionality
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestHuv(unittest.TestCase):
    """Test suite for huv functionality"""

    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test environments
        self.test_dir = Path(tempfile.mkdtemp(prefix="huv_test_"))
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Path to huv executable
        self.huv_path = Path(self.original_cwd) / "huv"
        self.assertTrue(self.huv_path.exists(), "huv executable not found")

    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def run_huv(self, args, expect_success=True):
        """Run huv command and return result"""
        cmd = [str(self.huv_path)] + args
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.test_dir)

        if expect_success and result.returncode != 0:
            self.fail(
                f"Command failed: {' '.join(cmd)}\nStdout: {result.stdout}\nStderr: {result.stderr}"
            )

        return result

    def test_help_command(self):
        """Test that help command works"""
        result = self.run_huv(["--help"])
        self.assertIn("Usage:", result.stdout)

    def test_create_standalone_venv(self):
        """Test creating a standalone virtual environment"""
        venv_name = "test_standalone"
        self.run_huv(["venv", venv_name])

        # Check that environment was created
        venv_path = self.test_dir / venv_name
        self.assertTrue(venv_path.exists())
        self.assertTrue((venv_path / "pyvenv.cfg").exists())
        self.assertTrue((venv_path / "bin" / "activate").exists())
        self.assertTrue((venv_path / "bin" / "python").exists())

    def test_create_hierarchical_venv(self):
        """Test creating a hierarchical virtual environment"""
        parent_name = "test_parent"
        child_name = "test_child"

        # Create parent environment
        self.run_huv(["venv", parent_name])

        # Create child environment with parent
        self.run_huv(["venv", child_name, "--parent", parent_name])

        # Verify both environments exist
        parent_path = self.test_dir / parent_name
        child_path = self.test_dir / child_name

        self.assertTrue(parent_path.exists())
        self.assertTrue(child_path.exists())

        # Verify child has hierarchy setup
        activate_script = child_path / "bin" / "activate"
        self.assertTrue(activate_script.exists())

        with open(activate_script) as f:
            content = f.read()
            self.assertIn("PARENT_VENV_PATH", content)
            self.assertIn(str(parent_path), content)

    def test_python_version_inheritance(self):
        """Test that child environments inherit parent Python version"""
        parent_name = "test_parent_version"
        child_name = "test_child_version"

        # Create parent environment
        self.run_huv(["venv", parent_name])

        # Create child environment (should inherit Python version)
        result = self.run_huv(["venv", child_name, "--parent", parent_name])

        # Check that the "Using parent's Python version" message appears
        self.assertIn("Using parent's Python version:", result.stdout)

        # Verify both environments have same Python version
        parent_cfg = self.test_dir / parent_name / "pyvenv.cfg"
        child_cfg = self.test_dir / child_name / "pyvenv.cfg"

        with open(parent_cfg) as f:
            parent_content = f.read()
        with open(child_cfg) as f:
            child_content = f.read()

        # Extract version_info from both
        parent_version = None
        child_version = None

        for line in parent_content.split("\n"):
            if line.startswith("version_info ="):
                parent_version = line.split("=")[1].strip()

        for line in child_content.split("\n"):
            if line.startswith("version_info ="):
                child_version = line.split("=")[1].strip()

        self.assertEqual(parent_version, child_version)

    def test_python_version_validation(self):
        """Test Python version validation with explicit version"""
        parent_name = "test_parent_validation"
        child_name = "test_child_validation"

        # Create parent environment
        self.run_huv(["venv", parent_name])

        # Get parent's Python version
        parent_cfg = self.test_dir / parent_name / "pyvenv.cfg"
        with open(parent_cfg) as f:
            content = f.read()

        parent_version = None
        for line in content.split("\n"):
            if line.startswith("version_info ="):
                version_parts = line.split("=")[1].strip().split(".")
                parent_version = f"{version_parts[0]}.{version_parts[1]}"
                break

        # Try to create child with same Python version (should work)
        self.run_huv(
            ["venv", child_name, "--parent", parent_name, "--python", parent_version]
        )
        child_path = self.test_dir / child_name
        self.assertTrue(child_path.exists())

    def test_invalid_parent_environment(self):
        """Test error handling for invalid parent environment"""
        child_name = "test_child_invalid"

        # Try to create child with non-existent parent
        result = self.run_huv(
            ["venv", child_name, "--parent", "nonexistent"], expect_success=False
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not exist", result.stderr)

    def test_existing_directory_error(self):
        """Test error handling when target directory already exists"""
        venv_name = "test_existing"

        # Create directory first
        (self.test_dir / venv_name).mkdir()

        # Try to create venv with same name
        result = self.run_huv(["venv", venv_name], expect_success=False)
        self.assertNotEqual(result.returncode, 0)

    def test_activate_this_py_modification(self):
        """Test that activate_this.py is properly modified for hierarchical environments"""
        parent_name = "test_activate_parent"
        child_name = "test_activate_child"

        # Create parent and child environments
        self.run_huv(["venv", parent_name])
        self.run_huv(["venv", child_name, "--parent", parent_name])

        # Check activate_this.py exists and has hierarchy setup
        activate_this = self.test_dir / child_name / "bin" / "activate_this.py"
        self.assertTrue(activate_this.exists())

        with open(activate_this) as f:
            content = f.read()
            self.assertIn("parent_venv_path", content)
            self.assertIn("site.addsitedir", content)
            self.assertIn("glob.glob", content)

    def test_uv_arguments_passthrough(self):
        """Test that uv arguments are properly passed through"""
        venv_name = "test_seed"

        # Create environment with --seed flag
        self.run_huv(["venv", venv_name, "--seed"])

        # Check that pip was installed (seed packages)
        venv_path = self.test_dir / venv_name
        pip_path = venv_path / "bin" / "pip"
        self.assertTrue(pip_path.exists())

    def test_hierarchical_with_additional_args(self):
        """Test hierarchical environment creation with additional uv arguments"""
        parent_name = "test_parent_args"
        child_name = "test_child_args"

        # Create parent and child with --seed
        self.run_huv(["venv", parent_name, "--seed"])
        self.run_huv(["venv", child_name, "--parent", parent_name, "--seed"])

        # Verify both have pip and hierarchy
        parent_pip = self.test_dir / parent_name / "bin" / "pip"
        child_pip = self.test_dir / child_name / "bin" / "pip"

        self.assertTrue(parent_pip.exists())
        self.assertTrue(child_pip.exists())

        # Verify hierarchy setup
        activate_script = self.test_dir / child_name / "bin" / "activate"
        with open(activate_script) as f:
            content = f.read()
            self.assertIn("PARENT_VENV_PATH", content)

    def test_multiple_hierarchy_levels(self):
        """Test creating multiple levels of hierarchy"""
        grandparent = "test_grandparent"
        parent = "test_parent_multi"
        child = "test_child_multi"

        # Create three-level hierarchy
        self.run_huv(["venv", grandparent])
        self.run_huv(["venv", parent, "--parent", grandparent])
        self.run_huv(["venv", child, "--parent", parent])

        # Verify all environments exist
        for env_name in [grandparent, parent, child]:
            env_path = self.test_dir / env_name
            self.assertTrue(env_path.exists())
            self.assertTrue((env_path / "pyvenv.cfg").exists())

    def test_get_python_version_helper(self):
        """Test the _get_python_version helper method"""
        venv_name = "test_version_helper"
        self.run_huv(["venv", venv_name])

        # Manually test the version extraction logic
        pyvenv_cfg = self.test_dir / venv_name / "pyvenv.cfg"
        self.assertTrue(pyvenv_cfg.exists())

        with open(pyvenv_cfg) as f:
            content = f.read()

        # Extract version using same logic as _get_python_version
        version = None
        for line in content.split("\n"):
            if line.startswith("version_info ="):
                version_str = line.split("=", 1)[1].strip()
                version_parts = version_str.split(".")
                if len(version_parts) >= 2:
                    version = f"{version_parts[0]}.{version_parts[1]}"
                break

        self.assertIsNotNone(version)
        if version is not None:
            self.assertRegex(version, r"^\d+\.\d+$")


class TestHuvIntegration(unittest.TestCase):
    """Integration tests that require uv to be installed"""

    @classmethod
    def setUpClass(cls):
        """Check if uv is available for integration tests"""
        try:
            subprocess.run(["uv", "--version"], capture_output=True, check=True)
            cls.uv_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            cls.uv_available = False

    def setUp(self):
        """Set up integration test environment"""
        if not self.uv_available:
            self.skipTest("uv not available for integration tests")

        self.test_dir = Path(tempfile.mkdtemp(prefix="huv_integration_"))
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        self.huv_path = Path(self.original_cwd) / "huv"

    def tearDown(self):
        """Clean up integration test environment"""
        if hasattr(self, "test_dir"):
            os.chdir(self.original_cwd)
            if self.test_dir.exists():
                shutil.rmtree(self.test_dir)

    def run_huv(self, args, expect_success=True):
        """Run huv command and return result"""
        cmd = [str(self.huv_path)] + args
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.test_dir)

        if expect_success and result.returncode != 0:
            self.fail(
                f"Command failed: {' '.join(cmd)}\nStdout: {result.stdout}\nStderr: {result.stderr}"
            )

        return result

    def test_uv_integration(self):
        """Test that huv works with actual uv installation"""
        venv_name = "test_uv_integration"
        result = self.run_huv(["venv", venv_name])

        # Verify uv was called and environment created
        self.assertIn("Creating virtual environment", result.stdout)

        venv_path = self.test_dir / venv_name
        self.assertTrue(venv_path.exists())
        self.assertTrue((venv_path / "pyvenv.cfg").exists())


if __name__ == "__main__":
    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHuv))
    suite.addTests(loader.loadTestsFromTestCase(TestHuvIntegration))

    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)

