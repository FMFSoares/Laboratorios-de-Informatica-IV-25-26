from __future__ import annotations

from app.schemas.fatura import FaturaResponse


def gerar_pdf_transferencia(pt) -> bytes:
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos

    NL  = {"new_x": XPos.LMARGIN, "new_y": YPos.NEXT}
    CNT = {"new_x": XPos.RIGHT,   "new_y": YPos.TOP}

    pdf = FPDF()
    pdf.set_margins(20, 20, 20)
    pdf.add_page()
    w = pdf.w - 40

    def line():
        pdf.set_draw_color(220, 220, 220)
        pdf.line(20, pdf.get_y(), pdf.w - 20, pdf.get_y())
        pdf.ln(5)

    def fmt_dt(dt):
        return dt.strftime("%d/%m/%Y %H:%M") if dt else "N/A"

    def safe(text: str) -> str:
        return text.encode("latin-1", errors="replace").decode("latin-1")

    # ── Header ────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(26, 188, 156)
    pdf.cell(w / 2, 10, "DLMCare", **CNT)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(w / 2, 10, pt.numero, align="R", **NL)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(w / 2, 5, "Documento de Transferência de Stock", **CNT)
    pdf.cell(w / 2, 5, fmt_dt(pt.data_pedido), align="R", **NL)

    pdf.ln(4)
    line()

    # ── Stores ───────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(w / 2, 5, "LOJA DE ORIGEM", **CNT)
    pdf.cell(w / 2, 5, "LOJA DE DESTINO", **NL)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(w / 2, 6, safe(pt.loja_origem.nome if pt.loja_origem else "N/A"), **CNT)
    pdf.cell(w / 2, 6, safe(pt.loja_destino.nome if pt.loja_destino else "N/A"), **NL)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(w / 2, 5, safe(f"Gerente: {pt.gerente_origem.nome if pt.gerente_origem else 'N/A'}"), **CNT)
    pdf.cell(w / 2, 5, safe(f"Gerente: {pt.gerente_destino.nome if pt.gerente_destino else 'N/A'}"), **NL)

    pdf.ln(4)
    line()

    # ── Part ─────────────────────────────────────────────────
    pdf.set_fill_color(249, 250, 251)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(w - 30, 7, "PEÇA", fill=True, **CNT)
    pdf.cell(30, 7, "QUANTIDADE", fill=True, align="R", **NL)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    peca_nome = safe(f"{pt.peca.referencia} - {pt.peca.nome}" if pt.peca else "N/A")
    pdf.cell(w - 30, 7, peca_nome, **CNT)
    pdf.cell(30, 7, str(pt.quantidade), align="R", **NL)

    pdf.ln(4)
    line()

    # ── Timeline ─────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(w, 5, "HISTÓRICO", **NL)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(w / 2, 5, f"Pedido em:          {fmt_dt(pt.data_pedido)}", **NL)
    pdf.cell(w / 2, 5, f"Resposta em:        {fmt_dt(pt.data_resposta)}", **NL)
    pdf.cell(w / 2, 5, f"Receção confirmada: {fmt_dt(pt.data_recepcao)}", **NL)

    pdf.ln(4)
    line()

    # ── Signatures ───────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(w / 2, 5, "ASSINATURA ORIGEM", **CNT)
    pdf.cell(w / 2, 5, "ASSINATURA DESTINO", **NL)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(50, 50, 50)
    if pt.data_assinatura_origem:
        pdf.cell(w / 2, 5, safe(pt.gerente_origem.nome if pt.gerente_origem else "N/A"), **CNT)
    else:
        pdf.set_text_color(180, 180, 180)
        pdf.cell(w / 2, 5, "Não assinado", **CNT)
        pdf.set_text_color(50, 50, 50)

    if pt.data_assinatura_destino:
        pdf.cell(w / 2, 5, safe(pt.gerente_destino.nome if pt.gerente_destino else "N/A"), **NL)
    else:
        pdf.set_text_color(180, 180, 180)
        pdf.cell(w / 2, 5, "Não assinado", **NL)
        pdf.set_text_color(50, 50, 50)

    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(120, 120, 120)
    if pt.data_assinatura_origem:
        pdf.cell(w / 2, 4, fmt_dt(pt.data_assinatura_origem), **CNT)
    else:
        pdf.cell(w / 2, 4, "", **CNT)
    if pt.data_assinatura_destino:
        pdf.cell(w / 2, 4, fmt_dt(pt.data_assinatura_destino), **NL)
    else:
        pdf.cell(w / 2, 4, "", **NL)

    # ── Footer ───────────────────────────────────────────────
    pdf.set_auto_page_break(False)
    pdf.set_y(-15)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(0, 5, f"Documento gerado automaticamente - Estado: {pt.estado.value}", align="C", **NL)

    return bytes(pdf.output())


def gerar_pdf_fatura(fatura: FaturaResponse) -> bytes:
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos

    NL  = {"new_x": XPos.LMARGIN, "new_y": YPos.NEXT}   # move to next line
    CNT = {"new_x": XPos.RIGHT,   "new_y": YPos.TOP}     # continue on same line

    pdf = FPDF()
    pdf.set_margins(20, 20, 20)
    pdf.add_page()
    w = pdf.w - 40

    def line():
        pdf.set_draw_color(220, 220, 220)
        pdf.line(20, pdf.get_y(), pdf.w - 20, pdf.get_y())
        pdf.ln(5)

    data_str = fatura.data_emissao.strftime("%d/%m/%Y")

    # ── Brand + invoice number ────────────────────────────────
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(26, 188, 156)
    pdf.cell(w / 2, 10, "DLMCare", **CNT)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(w / 2, 10, fatura.numero, align="R", **NL)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)

    pdf.cell(w / 2, 5, fatura.loja.nome, **CNT)
    pdf.cell(w / 2, 5, data_str, align="R", **NL)

    pdf.cell(w / 2, 5, fatura.loja.morada, **CNT)
    pdf.cell(w / 2, 5, f"Estado: {fatura.estado.value}", align="R", **NL)

    pdf.cell(0, 5, f"Tel. {fatura.loja.telefone}", **NL)

    pdf.ln(4)
    line()

    # ── Client + Scooter ────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(w / 2, 5, "CLIENTE", **CNT)
    pdf.cell(w / 2, 5, "TROTINETE", **NL)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(w / 2, 6, fatura.cliente.nome, **CNT)
    pdf.cell(w / 2, 6, f"{fatura.trotinete.marca} {fatura.trotinete.modelo}", **NL)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(w / 2, 5, f"NIF: {fatura.cliente.nif}", **CNT)
    pdf.cell(w / 2, 5, f"S/N: {fatura.trotinete.numero_serie}", **NL)

    if fatura.cliente.morada:
        pdf.cell(w / 2, 5, fatura.cliente.morada, **NL)

    pdf.ln(4)
    line()

    # ── Service line ────────────────────────────────────────────
    pdf.set_fill_color(249, 250, 251)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(w - 30, 7, "DESCRICAO DO SERVICO", fill=True, **CNT)
    pdf.cell(30, 7, "VALOR", fill=True, align="R", **NL)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(w - 30, 7, fatura.servico.descricao[:80], **CNT)
    pdf.cell(30, 7, f"{fatura.servico.preco_servico:.2f} EUR", align="R", **NL)

    # ── Parts table ─────────────────────────────────────────────
    if fatura.pecas_aplicadas:
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(w - 65, 7, "PECA", fill=True, **CNT)
        pdf.cell(15, 7, "QTD", fill=True, align="C", **CNT)
        pdf.cell(25, 7, "P. UNIT.", fill=True, align="R", **CNT)
        pdf.cell(25, 7, "SUBTOTAL", fill=True, align="R", **NL)

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(50, 50, 50)
        for p in fatura.pecas_aplicadas:
            pdf.cell(w - 65, 6, p.peca_nome[:50], **CNT)
            pdf.cell(15, 6, str(p.quantidade), align="C", **CNT)
            pdf.cell(25, 6, f"{p.preco_venda_unitario:.2f}", align="R", **CNT)
            pdf.cell(25, 6, f"{p.subtotal:.2f} EUR", align="R", **NL)

    pdf.ln(4)
    line()

    # ── Totals ───────────────────────────────────────────────────
    right_x = pdf.w - 20 - 65

    if fatura.pecas_aplicadas:
        pdf.set_x(right_x)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(40, 6, "Servico", **CNT)
        pdf.cell(25, 6, f"{fatura.servico.preco_servico:.2f} EUR", align="R", **NL)

        pdf.set_x(right_x)
        pdf.cell(40, 6, "Pecas", **CNT)
        pdf.cell(25, 6, f"{fatura.subtotal_pecas:.2f} EUR", align="R", **NL)

    if fatura.valor_desconto and fatura.valor_desconto > 0:
        label = (
            f"Desconto ({fatura.desconto_valor:.0f}%)"
            if fatura.desconto_tipo and fatura.desconto_tipo.value == "PERCENTUAL"
            else "Desconto"
        )
        pdf.set_x(right_x)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(220, 50, 50)
        pdf.cell(40, 6, label, **CNT)
        pdf.cell(25, 6, f"-{fatura.valor_desconto:.2f} EUR", align="R", **NL)

    pdf.set_x(right_x)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(40, 8, "TOTAL", **CNT)
    pdf.cell(25, 8, f"{fatura.valor_final:.2f} EUR", align="R", **NL)

    # ── Footer ────────────────────────────────────────────────────
    pdf.set_auto_page_break(False)
    pdf.set_y(-15)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(0, 5, f"Documento gerado automaticamente - OS #{fatura.ordem_servico_id}", align="C", **NL)

    return bytes(pdf.output())
