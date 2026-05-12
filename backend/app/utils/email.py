from __future__ import annotations

import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings


def send_email(
    to: str,
    subject: str,
    body_html: str,
    attachment_bytes: bytes | None = None,
    attachment_filename: str | None = None,
) -> None:
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to

    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(body_html, "html"))
    msg.attach(alt)

    if attachment_bytes and attachment_filename:
        part = MIMEApplication(attachment_bytes, _subtype="pdf")
        part.add_header("Content-Disposition", "attachment", filename=attachment_filename)
        msg.attach(part)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, to, msg.as_string())


def enviar_fatura_email(
    cliente_email: str,
    cliente_nome: str,
    fatura_numero: str,
    loja_nome: str,
    loja_telefone: str,
    pdf_bytes: bytes,
) -> None:
    subject = f"A sua fatura — {fatura_numero}"
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto;">
        <div style="background-color: #1abc9c; padding: 24px; text-align: center;">
          <h1 style="color: white; margin: 0;">DLMCare</h1>
        </div>
        <div style="padding: 32px;">
          <p>Olá, <strong>{cliente_nome}</strong>,</p>
          <p>
            Segue em anexo a sua fatura referente ao serviço de reparação da sua trotinete.
          </p>
          <div style="background-color: #f4f4f4; border-radius: 8px; padding: 16px; margin: 24px 0;">
            <p style="margin: 0;"><strong>Número de fatura:</strong> {fatura_numero}</p>
            <p style="margin: 8px 0 0;"><strong>Loja:</strong> {loja_nome}</p>
            <p style="margin: 8px 0 0;"><strong>Contacto:</strong> {loja_telefone}</p>
          </div>
          <p>
            O documento PDF está em anexo a este email. Se tiver alguma questão,
            não hesite em contactar-nos pelo número acima.
          </p>
          <p>Obrigado pela sua confiança,<br><strong>Equipa DLMCare</strong></p>
        </div>
        <div style="background-color: #f0f0f0; padding: 16px; text-align: center; font-size: 12px; color: #888;">
          Este email foi enviado automaticamente. Por favor não responda a este endereço.
        </div>
      </body>
    </html>
    """
    send_email(
        to=cliente_email,
        subject=subject,
        body_html=body_html,
        attachment_bytes=pdf_bytes,
        attachment_filename=f"{fatura_numero}.pdf",
    )


def notificar_trotinete_pronta(
    cliente_email: str,
    cliente_nome: str,
    os_numero: str,
    loja_nome: str,
    loja_telefone: str,
) -> None:
    subject = f"A sua trotinete está pronta para levantamento — {os_numero}"
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto;">
        <div style="background-color: #1abc9c; padding: 24px; text-align: center;">
          <h1 style="color: white; margin: 0;">DLMCare</h1>
        </div>
        <div style="padding: 32px;">
          <p>Olá, <strong>{cliente_nome}</strong>,</p>
          <p>
            A sua trotinete já se encontra reparada e pronta para levantamento na nossa oficina.
          </p>
          <div style="background-color: #f4f4f4; border-radius: 8px; padding: 16px; margin: 24px 0;">
            <p style="margin: 0;"><strong>Ordem de serviço:</strong> {os_numero}</p>
            <p style="margin: 8px 0 0;"><strong>Loja:</strong> {loja_nome}</p>
            <p style="margin: 8px 0 0;"><strong>Contacto:</strong> {loja_telefone}</p>
          </div>
          <p>
            Por favor dirija-se à loja durante o horário de funcionamento para proceder ao levantamento.
            Se tiver alguma questão, não hesite em contactar-nos pelo número acima.
          </p>
          <p>Obrigado pela sua confiança,<br><strong>Equipa DLMCare</strong></p>
        </div>
        <div style="background-color: #f0f0f0; padding: 16px; text-align: center; font-size: 12px; color: #888;">
          Este email foi enviado automaticamente. Por favor não responda a este endereço.
        </div>
      </body>
    </html>
    """
    send_email(to=cliente_email, subject=subject, body_html=body_html)


def notificar_os_cancelada(
    cliente_email: str,
    cliente_nome: str,
    os_numero: str,
    loja_nome: str,
    loja_telefone: str,
) -> None:
    subject = f"Ordem de serviço cancelada — {os_numero}"
    body_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto;">
        <div style="background-color: #1abc9c; padding: 24px; text-align: center;">
          <h1 style="color: white; margin: 0;">DLMCare</h1>
        </div>
        <div style="padding: 32px;">
          <p>Olá, <strong>{cliente_nome}</strong>,</p>
          <p>
            Informamos que a ordem de serviço relativa à sua trotinete foi cancelada.
          </p>
          <div style="background-color: #f4f4f4; border-radius: 8px; padding: 16px; margin: 24px 0;">
            <p style="margin: 0;"><strong>Ordem de serviço:</strong> {os_numero}</p>
            <p style="margin: 8px 0 0;"><strong>Loja:</strong> {loja_nome}</p>
            <p style="margin: 8px 0 0;"><strong>Contacto:</strong> {loja_telefone}</p>
          </div>
          <p>
            Se tiver alguma questão ou pretender reagendar o serviço, por favor contacte-nos
            pelo número acima. Pedimos desculpa por qualquer inconveniente.
          </p>
          <p>Obrigado pela sua compreensão,<br><strong>Equipa DLMCare</strong></p>
        </div>
        <div style="background-color: #f0f0f0; padding: 16px; text-align: center; font-size: 12px; color: #888;">
          Este email foi enviado automaticamente. Por favor não responda a este endereço.
        </div>
      </body>
    </html>
    """
    send_email(to=cliente_email, subject=subject, body_html=body_html)
