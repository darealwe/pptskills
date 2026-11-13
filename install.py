#!/usr/bin/env python3
"""Install the bundled local skill without replacing existing files."""
import argparse
import os
from pathlib import Path
import shutil
import sys


def install(destination):
    source = Path(__file__).resolve().parent / "skills" / "ppt-visual-expert-lite"
    if not (source / "SKILL.md").is_file():
        raise ValueError("技能文件不完整，请重新下载并解压整个仓库。")
    source_files = {}
    for item in source.rglob("*"):
        if item.is_symlink():
            raise ValueError("安装包包含符号链接，已停止。")
        if item.is_file():
            source_files[item.relative_to(source)] = item.read_bytes()
    target = destination.expanduser() / source.name
    if target.is_symlink():
        raise ValueError("目标是符号链接，已停止；不会覆盖。")
    if target.exists():
        if not target.is_dir():
            raise ValueError("目标位置已存在同名文件；不会覆盖。")
        items = list(target.rglob("*"))
        if any(item.is_symlink() for item in items):
            raise ValueError("目标包含符号链接，已停止；不会覆盖。")
        installed = {item.relative_to(target): item.read_bytes()
                     for item in items if item.is_file()}
        if installed == source_files:
            print("已安装相同版本，无需重复安装。")
            return
        raise ValueError("已存在不同内容的同名技能，请核对或备份后再安装；不会覆盖。")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)
    print("安装完成：" + str(target))
    print("请新开 Codex 对话，使用 $ppt-visual-expert-lite。")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    default_root = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    parser.add_argument("--dest", type=Path, default=default_root / "skills",
                        help="技能父目录，默认 CODEX_HOME/skills 或 ~/.codex/skills")
    args = parser.parse_args()
    try:
        install(args.dest)
    except (OSError, ValueError) as error:
        print("安装未完成：" + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
