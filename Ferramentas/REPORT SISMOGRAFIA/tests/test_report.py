from __future__ import annotations

from pathlib import Path

from src.config_loader import load_config
from src import report


def test_first_page_layout_reserves_footer_clearance():
    layout = report._first_page_layout()

    last_card_y = layout["first_card_y"] - (report.FIRST_PAGE_CARD_SLOTS - 1) * (
        layout["card_height"] + layout["card_gap"]
    )

    assert last_card_y >= report.FIRST_PAGE_LAST_CARD_Y
    assert layout["points_title_y"] > 260
    assert layout["chart_y"] > layout["points_title_y"]
    assert layout["chart_h"] > 0
    assert layout["charts_top_limit"] < 488


def test_restored_point_card_dimensions_match_original_pattern():
    assert report.POINT_CARD_HEIGHT == 58
    assert report.POINT_CARD_GAP == 14


def test_first_page_layout_integrates_both_chart_cards():
    layout = report._first_page_layout()
    chart_width = (report.PAGE_W - 2 * 28 - 14) / 2
    assert chart_width > 240
    assert layout["chart_h"] >= 140


def test_chart_height_contract_is_shared_by_python_and_web_layout():
    config = load_config(Path("config.json"))
    layout = report._first_page_layout(config)

    assert config["charts"]["figure_height"] == 5.0
    assert config["charts"]["web_figure_width"] == 6.5
    assert config["report_layout"]["chart_to_points_gap"] == 16
    assert layout["chart_h"] == 174
    assert layout["chart_y"] + layout["chart_h"] == layout["charts_top_limit"]


def test_point_status_text_uses_original_badge_labels():
    assert report._point_status_text({"evaluation": {"overall_conforme_abnt": True}}) == (
        "CONFORME ABNT",
        report.COLORS["green"],
    )
    assert report._point_status_text({"evaluation": {"overall_conforme_abnt": False}}) == (
        "VERIFICAR",
        report.COLORS["red"],
    )
