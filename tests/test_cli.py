"""
Tests for CLI interface
"""

from click.testing import CliRunner

from paper2epub.cli import main


class TestCLI:
    """Test suite for CLI"""

    def test_help(self):
        """Test help command"""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "paper2epub" in result.output

    def test_version(self):
        """Test version command"""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0

    def test_missing_file(self):
        """Test with non-existent file"""
        runner = CliRunner()
        result = runner.invoke(main, ["nonexistent.pdf"])
        assert result.exit_code != 0
