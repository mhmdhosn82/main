"""
Export utilities for generating Excel and PDF reports.
"""

import pandas as pd
from typing import List, Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
import arabic_reshaper
from bidi.algorithm import get_display
import os


def reshape_persian_text(text: str) -> str:
    """
    Reshape Persian/Arabic text for proper display in PDF.
    
    Args:
        text: Persian text
        
    Returns:
        Reshaped text
    """
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)


def export_to_excel(data: List[Dict[str, Any]], filename: str, sheet_name: str = "Sheet1"):
    """
    Export data to an Excel file.
    
    Args:
        data: List of dictionaries containing data
        filename: Output filename
        sheet_name: Sheet name in Excel file
    """
    if not data:
        return
    
    df = pd.DataFrame(data)
    
    # Save to Excel
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)


def export_policies_to_excel(policies: List[Dict[str, Any]], filename: str):
    """
    Export policies to Excel.
    
    Args:
        policies: List of policy dictionaries
        filename: Output filename
    """
    export_data = []
    for policy in policies:
        export_data.append({
            'شماره بیمه‌نامه': policy.get('policy_number', ''),
            'نام بیمه‌شده': policy.get('insured_name', ''),
            'تاریخ صدور': policy.get('issuance_date', ''),
            'تاریخ انقضا': policy.get('expiration_date', ''),
            'مبلغ پیش‌پرداخت': policy.get('advance_payment', 0),
            'مجموع اقساط': policy.get('total_installment_amount', 0),
            'تعداد اقساط': policy.get('number_of_installments', 0),
        })
    
    export_to_excel(export_data, filename, "بیمه‌نامه‌ها")


def export_installments_to_excel(installments: List[Dict[str, Any]], filename: str):
    """
    Export installments to Excel.
    
    Args:
        installments: List of installment dictionaries
        filename: Output filename
    """
    export_data = []
    for inst in installments:
        export_data.append({
            'شماره بیمه‌نامه': inst.get('policy_number', ''),
            'نام بیمه‌شده': inst.get('insured_name', ''),
            'شماره قسط': inst.get('installment_number', ''),
            'تاریخ سررسید': inst.get('due_date', ''),
            'مبلغ': inst.get('amount', 0),
            'وضعیت': 'پرداخت شده' if inst.get('status') == 'paid' else 'پرداخت نشده',
            'تاریخ پرداخت': inst.get('paid_date', ''),
        })
    
    export_to_excel(export_data, filename, "اقساط")


def export_to_pdf(data: List[List[str]], headers: List[str], filename: str, title: str):
    """
    Export data to a PDF file with Persian text support.
    
    Args:
        data: List of lists containing row data
        headers: List of header strings
        filename: Output filename
        title: Document title
    """
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []
    
    # Title
    title_text = reshape_persian_text(title)
    title_para = Paragraph(title_text, getSampleStyleSheet()['Title'])
    elements.append(title_para)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Prepare table data with reshaped Persian text
    table_data = [[reshape_persian_text(h) for h in headers]]
    for row in data:
        table_data.append([reshape_persian_text(str(cell)) for cell in row])
    
    # Create table
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)


def export_policies_to_pdf(policies: List[Dict[str, Any]], filename: str):
    """
    Export policies to PDF.
    
    Args:
        policies: List of policy dictionaries
        filename: Output filename
    """
    headers = ['شماره بیمه‌نامه', 'نام بیمه‌شده', 'تاریخ صدور', 'تاریخ انقضا', 
               'پیش‌پرداخت', 'مجموع اقساط', 'تعداد اقساط']
    
    data = []
    for policy in policies:
        data.append([
            policy.get('policy_number', ''),
            policy.get('insured_name', ''),
            policy.get('issuance_date', ''),
            policy.get('expiration_date', ''),
            str(policy.get('advance_payment', 0)),
            str(policy.get('total_installment_amount', 0)),
            str(policy.get('number_of_installments', 0))
        ])
    
    export_to_pdf(data, headers, filename, "لیست بیمه‌نامه‌ها")


def export_installments_to_pdf(installments: List[Dict[str, Any]], filename: str):
    """
    Export installments to PDF.
    
    Args:
        installments: List of installment dictionaries
        filename: Output filename
    """
    headers = ['شماره بیمه‌نامه', 'نام بیمه‌شده', 'شماره قسط', 
               'تاریخ سررسید', 'مبلغ', 'وضعیت']
    
    data = []
    for inst in installments:
        status = 'پرداخت شده' if inst.get('status') == 'paid' else 'پرداخت نشده'
        data.append([
            inst.get('policy_number', ''),
            inst.get('insured_name', ''),
            str(inst.get('installment_number', '')),
            inst.get('due_date', ''),
            str(inst.get('amount', 0)),
            status
        ])
    
    export_to_pdf(data, headers, filename, "لیست اقساط")
