import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from main import is_skipped, parse, run_command, run_script

def test_parse_simple_command():
    assert parse("ls /tmp") == ["ls", "/tmp"]

def test_parse_empty_line():
    assert parse("") == []

def test_parse_expands_environment_variable(monkeypatch):
    monkeypatch.setenv("MYVAR", "/home/user")
    assert parse("cd $MYVAR") == ["cd", "/home/user"]

def test_parse_quoted_arguments():
    assert parse('ls "my file"') == ["ls", "my file"]

def test_run_command_exit_returns_false():
    assert run_command("exit", []) is False

def test_run_command_unknown_returns_true(capsys):
    assert run_command("foo", []) is True
    captured = capsys.readouterr()
    assert "команда не найдена" in captured.out

def test_run_command_cd_too_many_args(capsys):
    run_command("cd", ["a", "b"])
    captured = capsys.readouterr()
    assert "слишком много аргументов" in captured.out

def test_run_command_ls_prints_args(capsys):
    run_command("ls", ["/tmp"])
    captured = capsys.readouterr()
    assert "ls" in captured.out
    assert "/tmp" in captured.out

def test_is_skipped_comment_line():
    assert is_skipped("# это комментарий") is True

def test_is_skipped_empty_line():
    assert is_skipped("   ") is True

def test_is_skipped_real_command():
    assert is_skipped("ls /tmp") is False

def test_run_script_shows_input_and_output(tmp_path, capsys):
    script = tmp_path / "script.txt"
    script.write_text("# комментарий\nls /tmp\nexit\n", encoding="utf-8")
    running = run_script(str(script))
    captured = capsys.readouterr()
    assert running is False
    assert "vfs$ ls /tmp" in captured.out
    assert "ls ['/tmp']" in captured.out

def test_run_script_missing_file_exits(tmp_path):
    missing = tmp_path / "no_such_file.txt"
    try:
        run_script(str(missing))
        assert False, "ожидался SystemExit"
    except SystemExit as err:
        assert err.code == 1
