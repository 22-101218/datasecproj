"""
pdf_cert.py
===========
Generate a printable PDF ownership certificate for any registered vehicle.

Usage:
    from pdf_cert import generate_certificate
    path = generate_certificate("1HGBH41JXMN109186")
    # path = "certificate_1HGBH41JXMN109186.pdf"

Requires: reportlab, qrcode[pil], Pillow
"""

from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path

import qrcode
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    Image,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from vehiclechain.blockchain import get_vehicle, get_history, w3
from vehiclechain.paths import data_root, logo_path

OUTPUT_DIR = data_root()
LOGO_PATH = logo_path()

# ── Colour palette ───────────────────────────────────────────────────────────
RED      = colors.HexColor("#D32F2F")
RED_DARK = colors.HexColor("#B71C1C")
GREY_TEXT = colors.HexColor("#616161")
BLACK    = colors.HexColor("#212121")
WHITE    = colors.white
LIGHT_BG = colors.HexColor("#FFFFFF")
ALT_BG   = colors.HexColor("#F9F9F9")
INFO_LABEL_BG = colors.HexColor("#F2F2F2")
BORDER   = colors.HexColor("#E0E0E0")

# Printable width matches SimpleDocTemplate left+right margins (1.8 cm each).
PAGE_TEXT_WIDTH = A4[0] - 3.6 * cm


def _make_qr_image(data: str, size: int = 150) -> Image:
    """Render a QR code into a ReportLab Image flowable."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    pil_img = qr.make_image(fill_color="#D32F2F", back_color="#FFFFFF").convert("RGB")
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    buf.seek(0)
    return Image(buf, width=size, height=size)


def _fmt_ts(ts: int) -> str:
    """Convert a UNIX timestamp to a human-readable string."""
    try:
        return datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return str(ts)

def _make_logo(width_cm: float = 3.0) -> Image | None:
    if not LOGO_PATH.exists():
        return None
    with PILImage.open(LOGO_PATH) as img:
        w, h = img.size
    if w == 0:
        return None
    width = width_cm * cm
    height = width * (h / w)
    return Image(str(LOGO_PATH), width=width, height=height)


def generate_certificate(vehicle_id: str) -> str:
    """
    Generate a PDF certificate for *vehicle_id*.

    Returns the absolute path to the saved PDF file.
    Raises RuntimeError if the vehicle is not found or contract not deployed.
    """
    # ── Fetch on-chain data ──────────────────────────────────────────────────
    vehicle = get_vehicle(vehicle_id)
    history = get_history(vehicle_id)
    block_number = w3.eth.block_number

    # ── Output path ─────────────────────────────────────────────────────────
    safe_id = "".join(c if c.isalnum() else "_" for c in vehicle_id)
    certs_dir = OUTPUT_DIR / "certificates"
    certs_dir.mkdir(exist_ok=True)
    
    from datetime import datetime as dt
    timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
    out_path = certs_dir / f"certificate_{safe_id}_{timestamp}.pdf"

    # ── Document setup ───────────────────────────────────────────────────────
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    # Header: logo left, title + subtitle lines right.
    header_title_style = ParagraphStyle(
        "CertTitleHdr",
        fontSize=20,
        textColor=RED,
        alignment=TA_LEFT,
        fontName="Helvetica-Bold",
        leading=26,
        spaceAfter=8,
        spaceBefore=0,
    )
    header_sub_style = ParagraphStyle(
        "CertSubHdr",
        fontSize=10,
        textColor=GREY_TEXT,
        alignment=TA_LEFT,
        fontName="Helvetica",
        leading=14,
        spaceAfter=3,
        spaceBefore=0,
    )
    # Vehicle details table only (left-aligned like print preview).
    info_label_style = ParagraphStyle(
        "InfoLabel",
        fontSize=8,
        textColor=GREY_TEXT,
        fontName="Helvetica-Bold",
        alignment=TA_LEFT,
    )
    info_body_style = ParagraphStyle(
        "InfoBody",
        fontSize=9,
        textColor=BLACK,
        fontName="Helvetica",
        leading=14,
        alignment=TA_LEFT,
    )
    info_mono_style = ParagraphStyle(
        "InfoMono",
        fontSize=8,
        textColor=RED_DARK,
        fontName="Courier",
        leading=12,
        alignment=TA_LEFT,
    )
    section_style = ParagraphStyle(
        "Section",
        fontSize=11,
        textColor=RED_DARK,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "Body",
        fontSize=9,
        textColor=BLACK,
        fontName="Helvetica",
        leading=14,
        alignment=TA_CENTER,
    )
    mono_style = ParagraphStyle(
        "Mono",
        fontSize=8,
        textColor=RED_DARK,
        fontName="Courier",
        leading=12,
        alignment=TA_CENTER,
    )
    label_style = ParagraphStyle(
        "Label",
        fontSize=8,
        textColor=GREY_TEXT,
        fontName="Helvetica",
        alignment=TA_LEFT,
    )
    proof_label_style = ParagraphStyle(
        "ProofLabel",
        fontSize=8,
        textColor=GREY_TEXT,
        fontName="Helvetica",
        alignment=TA_LEFT,
    )
    proof_body_style = ParagraphStyle(
        "ProofBody",
        fontSize=9,
        textColor=BLACK,
        fontName="Helvetica",
        leading=14,
        alignment=TA_LEFT,
    )
    proof_mono_style = ParagraphStyle(
        "ProofMono",
        fontSize=8,
        textColor=RED_DARK,
        fontName="Courier",
        leading=12,
        alignment=TA_LEFT,
    )
    # History table header: must set text to white here — Paragraph color overrides Table TEXTCOLOR.
    hist_header_style = ParagraphStyle(
        "HistHeader",
        fontSize=9,
        textColor=WHITE,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        leading=11,
    )
    footer_style = ParagraphStyle(
        "Footer",
        fontSize=7,
        textColor=GREY_TEXT,
        alignment=TA_CENTER,
        fontName="Helvetica",
    )

    story = []

    # ── Header: car logo left, certificate title + lines right ───────────────
    story.append(Spacer(1, 0.25 * cm))
    logo = _make_logo(width_cm=2.6)
    logo_col_w = 3.15 * cm
    text_w = PAGE_TEXT_WIDTH - logo_col_w if logo else PAGE_TEXT_WIDTH

    # Explicit line break avoids bad wraps; leading prevents overlapping baselines.
    title_txt = "BLOCKCHAIN VEHICLE<br/>OWNERSHIP CERTIFICATE"
    title_block = [
        [Paragraph(title_txt, header_title_style)],
        [Paragraph("Issued by the Decentralized Transport Authority", header_sub_style)],
        [Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", header_sub_style)],
    ]
    text_stack = Table(title_block, colWidths=[text_w])
    text_stack.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    if logo:
        header_row = Table([[logo, text_stack]], colWidths=[logo_col_w, text_w])
        header_row.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "LEFT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (0, 0), 10),
            ("RIGHTPADDING", (1, 0), (1, 0), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(header_row)
    else:
        story.append(text_stack)
    story.append(HRFlowable(width="100%", thickness=1, color=RED, spaceAfter=12))

    # ── Vehicle info table (left column grey labels) + QR on the right ───────
    qr_img = _make_qr_image(vehicle_id, size=130)
    info_col_label_w = 3.7 * cm
    info_col_value_w = 8.8 * cm
    info_table_w = info_col_label_w + info_col_value_w

    info_data = [
        [Paragraph("VEHICLE ID", info_label_style),   Paragraph(vehicle["vehicle_id"], info_mono_style)],
        [Paragraph("BRAND", info_label_style),         Paragraph(vehicle["brand"] or "—", info_body_style)],
        [Paragraph("MODEL", info_label_style),         Paragraph(vehicle["model"] or "—", info_body_style)],
        [Paragraph("REGISTERED", info_label_style),    Paragraph(_fmt_ts(vehicle["registered_at"]), info_body_style)],
        [Paragraph("CURRENT OWNER", info_label_style), Paragraph(vehicle["current_owner"], info_mono_style)],
    ]
    info_table = Table(
        info_data,
        colWidths=[info_col_label_w, info_col_value_w],
    )
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), INFO_LABEL_BG),
        ("BACKGROUND", (1, 0), (1, -1), WHITE),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    layout = Table(
        [[info_table, qr_img]],
        colWidths=[info_table_w, PAGE_TEXT_WIDTH - info_table_w],
    )
    layout.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(layout)
    story.append(Spacer(1, 0.4 * cm))

    # ── Ownership history ────────────────────────────────────────────────────
    story.append(Paragraph("OWNERSHIP HISTORY", section_style))

    if history:
        hist_header = [
            Paragraph("#", hist_header_style),
            Paragraph("OWNER ADDRESS", hist_header_style),
            Paragraph("TIMESTAMP", hist_header_style),
            Paragraph("EVENT", hist_header_style),
        ]
        hist_rows = [hist_header]
        for i, rec in enumerate(history):
            event = "REGISTERED" if i == 0 else "TRANSFERRED"
            color = RED if i == 0 else RED_DARK
            hist_rows.append([
                Paragraph(str(i + 1), body_style),
                Paragraph(rec["owner"], mono_style),
                Paragraph(_fmt_ts(rec["transferred_at"]), body_style),
                Paragraph(
                    event,
                    ParagraphStyle(
                        f"e{i}",
                        fontSize=8,
                        textColor=color,
                        fontName="Helvetica-Bold",
                        alignment=TA_CENTER,
                    ),
                ),
            ])

        hist_table = Table(
            hist_rows,
            colWidths=[1 * cm, 8.5 * cm, 5.5 * cm, 2.5 * cm],
        )
        hist_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), RED),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, ALT_BG]),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 1), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ]))
        story.append(hist_table)
    else:
        story.append(Paragraph("No history records found.", body_style))

    # ── Blockchain proof ──────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 0.2 * cm))

    proof_data = [
        [
            Paragraph("VERIFIED ON", proof_label_style),
            Paragraph("Ganache Local Blockchain (Chain ID: 1337)", proof_body_style),
        ],
        [
            Paragraph("BLOCK NUMBER", proof_label_style),
            Paragraph(f"#{block_number}", proof_mono_style),
        ],
        [
            Paragraph("TOTAL TRANSFERS", proof_label_style),
            Paragraph(str(max(0, len(history) - 1)), proof_body_style),
        ],
        [
            Paragraph("IMMUTABLE SINCE", proof_label_style),
            Paragraph(_fmt_ts(vehicle["registered_at"]), proof_body_style),
        ],
    ]
    proof_table = Table(proof_data, colWidths=[3.5 * cm, 14 * cm])
    proof_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_BG, ALT_BG]),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(proof_table)

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "This certificate is generated from immutable blockchain records. "
        "All ownership transfers are permanently recorded and cannot be altered or deleted.",
        footer_style,
    ))

    # ── Build PDF ─────────────────────────────────────────────────────────────
    def _page_background(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(WHITE)
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        canvas.restoreState()

    doc.build(story, onFirstPage=_page_background, onLaterPages=_page_background)
    return str(out_path)
