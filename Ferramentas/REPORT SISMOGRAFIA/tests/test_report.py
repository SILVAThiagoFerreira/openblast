from __future__ import annotations

from src import report


def test_first_page_layout_reserves_footer_clearance():
    layout = report._first_page_layout()

    last_card_y = layout["first_card_y"] - (report.FIRST_PAGE_CARD_SLOTS - 1) * (
        layout["card_height"] + layout["card_gap"]
    )

    assert last_card_y >= report.FIRST_PAGE_LAST_CARD_Y
    assert layout["points_title_y"] > 360


def test_restored_point_card_dimensions_match_original_pattern():
    assert report.POINT_CARD_HEIGHT == 58
    assert report.POINT_CARD_GAP == 14


def test_chart_page_is_large_enough_for_readable_graphs():
    card_h = 300
    gap = 24
    top_y = report.PAGE_H - 86 - card_h
    bottom_y = top_y - gap - card_h
    assert top_y > bottom_y > 80


def test_point_status_text_uses_original_badge_labels():
    assert report._point_status_text({"evaluation": {"overall_conforme_abnt": True}}) == (
        "CONFORME ABNT",
        report.COLORS["green"],
    )
    assert report._point_status_text({"evaluation": {"overall_conforme_abnt": False}}) == (
        "VERIFICAR",
        report.COLORS["red"],
    )
