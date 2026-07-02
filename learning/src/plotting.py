"""离线教学用 matplotlib 中文字体安全配置。

本模块提供一套"永远不会崩溃"的 matplotlib 中文字体配置方案，
适合零基础学员在国内各种 Windows / macOS / Linux 环境下使用。

只要调用 configure_chinese_plotting() 一次，后续所有图表都会自动尝试
使用中文字体；如果当前系统没有任何中文字体，则静默回退到英文，不会抛出异常。
"""

from __future__ import annotations

import warnings
from typing import Any

try:
    import matplotlib.font_manager as font_manager
    import matplotlib.pyplot as plt

    _HAS_MATPLOTLIB = True
except ImportError:
    _HAS_MATPLOTLIB = False


# 中文字体候选列表（按优先级排序，均为各平台自带字体）
_CHINESE_FONT_CANDIDATES: list[str] = [
    "Microsoft YaHei",       # Windows 10/11 自带微软雅黑
    "SimHei",                 # Windows 传统黑体
    "Noto Sans CJK SC",       # Linux / Google 开源思源黑体
    "Arial Unicode MS",       # macOS 自带
]

# 最终后备字体（不支持中文，但保证程序不崩溃）
_FALLBACK_FONT: str = "DejaVu Sans"

# 模块内部状态
_FONT_CONFIG: dict[str, Any] = {
    "chinese_available": False,
    "selected_font": _FALLBACK_FONT,
    "fallback_reason": None,
}


def _is_font_available(font_name: str) -> bool:
    """检测指定字体是否在系统中可用。

    使用 matplotlib.font_manager.findfont 进行检测，
    不依赖任何硬编码路径或用户私有字体文件。
    """
    if not _HAS_MATPLOTLIB:
        return False
    try:
        font_manager.findfont(
            font_manager.FontProperties(family=font_name),
            fallback_to_default=False,
        )
        return True
    except Exception:
        return False


def configure_chinese_plotting() -> str:
    """配置 matplotlib 使其支持中文显示。

    按优先级尝试系统中可用的中文字体，找到第一个可用字体后立即采用。
    如果所有中文字体都不可用，则使用 DejaVu Sans 作为安全后备。

    零基础解释：调用一次这个函数后，matplotlib 画图时就能正常显示中文了。

    Returns:
        实际选用的字体名称（字符串）。如果选到了中文字体，返回该字体名；
        否则返回 "DejaVu Sans"。
    """
    global _FONT_CONFIG

    if not _HAS_MATPLOTLIB:
        _FONT_CONFIG.update({
            "chinese_available": False,
            "selected_font": _FALLBACK_FONT,
            "fallback_reason": "matplotlib 未安装",
        })
        return _FALLBACK_FONT

    # 按优先级依次检测中文字体
    for font_name in _CHINESE_FONT_CANDIDATES:
        if _is_font_available(font_name):
            plt.rcParams["font.sans-serif"] = [font_name, _FALLBACK_FONT]
            plt.rcParams["font.family"] = "sans-serif"
            plt.rcParams["axes.unicode_minus"] = False
            _FONT_CONFIG.update({
                "chinese_available": True,
                "selected_font": font_name,
                "fallback_reason": None,
            })
            return font_name

    # 没有任何中文字体可用：安全回退
    plt.rcParams["font.sans-serif"] = [_FALLBACK_FONT]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False
    _FONT_CONFIG.update({
        "chinese_available": False,
        "selected_font": _FALLBACK_FONT,
        "fallback_reason": "未检测到任何中文字体，已回退到 DejaVu Sans",
    })
    return _FALLBACK_FONT


def safe_title(ax: Any, title_cn: str, title_en: str) -> None:
    """安全设置图表标题。

    当中文字体可用时使用中文标题，否则自动回退到英文标题。
    不会因字体缺失而抛出异常或输出字体警告。

    零基础解释：不用自己判断系统有没有中文字体，这个函数帮你自动选择。

    Args:
        ax: matplotlib Axes 对象（即 plt.subplots() 返回的坐标轴）。
        title_cn: 中文标题文本。
        title_en: 英文标题文本（作为回退）。
    """
    if not _HAS_MATPLOTLIB:
        return

    if _FONT_CONFIG["chinese_available"]:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            ax.set_title(title_cn)
    else:
        ax.set_title(title_en)


def get_font_status() -> dict[str, Any]:
    """返回当前字体配置状态。

    可用于在 Notebook 中检查字体配置结果，方便教学演示。

    Returns:
        包含以下键的字典：
        - chinese_available (bool): 中文字体是否可用
        - selected_font (str): 当前实际选用的字体名称
        - fallback_reason (str | None): 回退原因，未发生回退时为 None
    """
    return {
        "chinese_available": _FONT_CONFIG["chinese_available"],
        "selected_font": _FONT_CONFIG["selected_font"],
        "fallback_reason": _FONT_CONFIG["fallback_reason"],
    }
