#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ocr_pdf.py — 将 PDF 的每一页渲染为高清 PNG 图片，供 OCR（光学字符识别）使用。

零配置说明（面向无编程基础的用户）：
    本脚本由 AI 助手在本地自动执行，最终用户全程无需安装或配置任何软件：
    1. 运行时自动检测所需依赖（PyMuPDF）；
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
import os
import subprocess
import sys


def ensure_dependencies() -> bool:
    """检测 PyMuPDF 是否可用；缺失时自动安装。返回最终是否可用。"""
    try:
        import fitz  # noqa: F401
        return True
    except ImportError:
        pass

    print("未检测到 PyMuPDF（PDF 渲染库），正在自动安装，请稍候……")
    print("提示：此过程由 AI 助手自动完成，无需用户手动操作。")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install",
             "--disable-pip-version-check", "PyMuPDF"],
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"自动安装失败：{exc}", file=sys.stderr)
        print(
            "提示：AI 助手将自动改用内置文档解析/图像识别能力完成 PDF 解析，"
            "本任务不会因此中断，用户无需做任何操作。",
            file=sys.stderr,
        )
        return False

    try:
        import fitz  # noqa: F401
        return True
    except ImportError:
        print("依赖安装后仍无法加载 PyMuPDF，请向 AI 助手反馈。", file=sys.stderr)
        return False


def check_only() -> int:
    """仅检查环境是否就绪。"""
    print(f"Python 版本：{sys.version.split()[0]}")
    try:
        import fitz
        print(f"PyMuPDF 版本：{fitz.__doc__ or '已安装'}")
        print("环境就绪：可以运行渲染。")
        return 0
    except ImportError:
        print("PyMuPDF 未安装（可由本脚本自动安装）。")
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

    if not ensure_dependencies():
        return 2

    import fitz  # 此时依赖已保证可用

    os.makedirs(args.out_dir, exist_ok=True)

    doc = fitz.open(args.pdf)
    total = len(doc)
    print(f"总页数: {total}")

    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=args.dpi)
        out_path = os.path.join(args.out_dir, f"p{i + 1:02d}.png")
        pix.save(out_path)
        print(f"{out_path}\t{pix.width}x{pix.height}")

    print("渲染完成。AI 助手将自动把以上 PNG 逐页（或整批）交给图像识别能力识别文字。")
    return 0


if __name__ == "__main__":
    sys.exit(main())