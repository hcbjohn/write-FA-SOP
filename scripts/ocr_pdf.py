#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ocr_pdf.py — 将 PDF 的每一页渲染为高清 PNG 图片，供 OCR（光学字符识别）使用。

零配置说明（面向无编程基础的用户）：
    本脚本由 AI 助手在本地自动执行，最终用户全程无需安装或配置任何软件：
    1. 运行时自动检测所需依赖（PyMuPDF），并同时兼容 pymupdf / fitz 两种导入名；
    2. 依赖缺失时自动安装（通过网络 pip 安装，无需用户手动操作）；
    3. 若自动安装失败（如离线/受限环境），脚本返回明确错误码，
       AI 助手会自动降级使用内置的文档解析与图像识别能力完成同样任务，流程不中断。

依赖：
    Python 3.8+（通常由 AI 助手软件自带运行时，用户无感知）
    PyMuPDF（本脚本会自动检测并自动安装）

用法：
    python ocr_pdf.py <pdf路径> [-o 输出目录] [--dpi 300]
    python ocr_pdf.py --check    # 仅检查环境是否就绪，不渲染
"""

import argparse
import importlib
import os
import subprocess
import sys


def _import_pymupdf():
    """按优先级尝试导入 PyMuPDF，兼容新旧两种模块名。

    - 新版（PyMuPDF >= 1.24）推荐 `import pymupdf`；
    - 旧版及历史脚本常用 `import fitz`。
    任一名称导入成功即返回模块；均失败返回 None。
    """
    for name in ("pymupdf", "fitz"):
        try:
            return importlib.import_module(name)
        except ImportError:
            continue
    return None


def _install_pymupdf() -> bool:
    """用当前解释器自动安装 PyMuPDF，成功返回 True。"""
    print("未检测到 PyMuPDF（PDF 渲染库），正在自动安装，请稍候……")
    print("提示：此过程由 AI 助手自动完成，无需用户手动操作。")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install",
             "--disable-pip-version-check", "--quiet", "PyMuPDF"],
        )
    except Exception as exc:  # noqa: BLE001
        print(f"自动安装失败：{exc}", file=sys.stderr)
        print(
            "提示：AI 助手将自动改用内置文档解析/图像识别能力完成 PDF 解析，"
            "本任务不会因此中断，用户无需做任何操作。",
            file=sys.stderr,
        )
        return False

    # 新安装的包需要刷新导入缓存，否则同进程内 import 仍可能失败
    importlib.invalidate_caches()
    return True


def ensure_module():
    """返回可用的 PyMuPDF 模块；必要时自动安装。失败返回 None。"""
    module = _import_pymupdf()
    if module is not None:
        return module

    if not _install_pymupdf():
        return None

    module = _import_pymupdf()
    if module is None:
        print("依赖安装后仍无法加载 PyMuPDF，请向 AI 助手反馈。", file=sys.stderr)
    return module


def check_only() -> int:
    """仅检查环境是否就绪（不安装、不渲染）。"""
    print(f"Python 版本：{sys.version.split()[0]}")
    print(f"解释器路径：{sys.executable}")
    module = _import_pymupdf()
    if module is not None:
        ver = getattr(module, "__version__", None) or getattr(module, "VersionBind", None)
        print(f"PyMuPDF 已就绪（导入名：{module.__name__}，版本：{ver or '未知'}）")
        print("环境就绪：可以运行渲染。")
        return 0
    print("PyMuPDF 尚未安装（本脚本首次渲染时会自动安装，用户无需操作）。")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="将 PDF 每页渲染为高清 PNG 图片，供 OCR 使用（零配置运行）。"
    )
    parser.add_argument("pdf", nargs="?", help="PDF 文件路径")
    parser.add_argument(
        "-o", "--out-dir", default="pdf_pages", help="图片输出目录（默认: pdf_pages）"
    )
    parser.add_argument("--dpi", type=int, default=300, help="渲染分辨率（默认: 300）")
    parser.add_argument(
        "--check", action="store_true",
        help="仅检查环境是否就绪（不渲染），返回 0 表示就绪"
    )
    args = parser.parse_args()

    if args.check:
        return check_only()

    if not args.pdf:
        parser.error("请提供 PDF 文件路径（或使用 --check 检查环境）")

    if not os.path.isfile(args.pdf):
        print(f"错误：找不到 PDF 文件：{args.pdf}", file=sys.stderr)
        return 1

    pymupdf = ensure_module()
    if pymupdf is None:
        return 2

    os.makedirs(args.out_dir, exist_ok=True)

    doc = pymupdf.open(args.pdf)
    total = doc.page_count
    print(f"总页数: {total}")

    for i in range(total):
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=args.dpi)
        out_path = os.path.join(args.out_dir, f"p{i + 1:02d}.png")
        pix.save(out_path)
        print(f"{out_path}\t{pix.width}x{pix.height}")

    doc.close()
    print("渲染完成。AI 助手将自动把以上 PNG 逐页（或整批）交给图像识别能力识别文字。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
