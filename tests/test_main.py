import os
import sys
import pytest
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from main import (
    VfsError,
    get_motd,
    is_skipped,
    load_vfs,
    parse,
    run_command,
    run_script,
    vfs_name_from_path,
)

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
    with pytest.raises(SystemExit) as err:
        run_script(str(missing))
    assert err.value.code == 1

def write_vfs(tmp_path, data):
    path = tmp_path / "test.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


def test_load_vfs_minimal(tmp_path):
    root = load_vfs(write_vfs(tmp_path, {"type": "dir", "children": {}}))
    assert root["type"] == "dir"


def test_load_vfs_file_not_found(tmp_path):
    with pytest.raises(VfsError, match="не найден"):
        load_vfs(str(tmp_path / "no_such.json"))


def test_load_vfs_invalid_json(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{ oops", encoding="utf-8")
    with pytest.raises(VfsError, match="неверный формат"):
        load_vfs(str(path))


def test_load_vfs_unknown_node_type(tmp_path):
    data = {"type": "dir", "children": {"a": {"type": "weird"}}}
    with pytest.raises(VfsError, match="неизвестный тип"):
        load_vfs(write_vfs(tmp_path, data))


def test_load_vfs_root_must_be_dir(tmp_path):
    data = {"type": "file", "content": "x"}
    with pytest.raises(VfsError, match="корень"):
        load_vfs(write_vfs(tmp_path, data))


def test_load_vfs_invalid_base64(tmp_path):
    file_node = {"type": "file", "encoding": "base64", "content": "!!!"}
    data = {"type": "dir", "children": {"b": file_node}}
    with pytest.raises(VfsError, match="base64"):
        load_vfs(write_vfs(tmp_path, data))

def test_get_motd_present():
    motd = {"type": "file", "content": "Привет\n"}
    root = {"type": "dir", "children": {"motd": motd}}
    assert get_motd(root) == "Привет\n"


def test_get_motd_base64():
    motd = {"type": "file", "encoding": "base64", "content": "SGk="}
    root = {"type": "dir", "children": {"motd": motd}}
    assert get_motd(root) == "Hi"


def test_get_motd_absent():
    assert get_motd({"type": "dir", "children": {}}) is None

def test_vfs_name_from_path():
    assert vfs_name_from_path("some/dir/my_vfs.json") == "my_vfs"


def test_vfs_name_from_path_simple():
    assert vfs_name_from_path("deep.json") == "deep"
