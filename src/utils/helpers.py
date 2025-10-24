"""
Utility functions for the Insurance Management System.
"""

import jdatetime
from datetime import datetime, timedelta
from typing import List
from src.models.models import Installment


def jalali_to_gregorian(jalali_date: str) -> datetime:
    """
    Convert Jalali (Solar Hijri) date string to Gregorian datetime.
    
    Args:
        jalali_date: Date string in format YYYY/MM/DD
        
    Returns:
        Gregorian datetime object
    """
    parts = jalali_date.split('/')
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    jdate = jdatetime.date(year, month, day)
    return jdate.togregorian()


def gregorian_to_jalali(gregorian_date: datetime) -> str:
    """
    Convert Gregorian datetime to Jalali (Solar Hijri) date string.
    
    Args:
        gregorian_date: Gregorian datetime object
        
    Returns:
        Date string in format YYYY/MM/DD
    """
    jdate = jdatetime.date.fromgregorian(date=gregorian_date)
    return jdate.strftime('%Y/%m/%d')


def get_current_jalali_date() -> str:
    """
    Get current date in Jalali (Solar Hijri) format.
    
    Returns:
        Current date string in format YYYY/MM/DD
    """
    return jdatetime.date.today().strftime('%Y/%m/%d')


def add_months_to_jalali_date(jalali_date: str, months: int) -> str:
    """
    Add months to a Jalali date.
    
    Args:
        jalali_date: Date string in format YYYY/MM/DD
        months: Number of months to add
        
    Returns:
        New date string in format YYYY/MM/DD
    """
    # Convert to Gregorian, add months, convert back
    greg_date = jalali_to_gregorian(jalali_date)
    
    # Calculate new month and year
    new_month = greg_date.month + months
    new_year = greg_date.year
    
    while new_month > 12:
        new_month -= 12
        new_year += 1
    
    while new_month < 1:
        new_month += 12
        new_year -= 1
    
    # Handle day overflow
    try:
        new_date = datetime(new_year, new_month, greg_date.day)
    except ValueError:
        # Day doesn't exist in new month, use last day of month
        if new_month == 12:
            new_date = datetime(new_year + 1, 1, 1) - timedelta(days=1)
        else:
            new_date = datetime(new_year, new_month + 1, 1) - timedelta(days=1)
    
    return gregorian_to_jalali(new_date)


def generate_installments(policy_id: int, issuance_date: str, 
                         number_of_installments: int, 
                         total_amount: float) -> List[Installment]:
    """
    Generate installments for a policy.
    
    Args:
        policy_id: The policy ID
        issuance_date: Policy issuance date in Jalali format
        number_of_installments: Number of installments to generate
        total_amount: Total amount to be divided
        
    Returns:
        List of Installment instances
    """
    installments = []
    amount_per_installment = total_amount / number_of_installments
    
    for i in range(number_of_installments):
        # Installments start one month after issuance
        due_date = add_months_to_jalali_date(issuance_date, i + 1)
        
        installment = Installment(
            policy_id=policy_id,
            installment_number=i + 1,
            due_date=due_date,
            amount=amount_per_installment,
            status='unpaid'
        )
        installments.append(installment)
    
    return installments


def format_currency(amount: float) -> str:
    """
    Format amount as currency with Persian separators.
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted currency string
    """
    return f"{amount:,.0f} ریال"


def is_date_in_range(date_str: str, start_date: str, end_date: str) -> bool:
    """
    Check if a date falls within a date range.
    
    Args:
        date_str: Date to check in Jalali format
        start_date: Start date in Jalali format
        end_date: End date in Jalali format
        
    Returns:
        True if date is in range, False otherwise
    """
    date = jalali_to_gregorian(date_str)
    start = jalali_to_gregorian(start_date)
    end = jalali_to_gregorian(end_date)
    
    return start <= date <= end


def compare_dates(date1: str, date2: str) -> int:
    """
    Compare two Jalali dates.
    
    Args:
        date1: First date in Jalali format
        date2: Second date in Jalali format
        
    Returns:
        -1 if date1 < date2, 0 if equal, 1 if date1 > date2
    """
    d1 = jalali_to_gregorian(date1)
    d2 = jalali_to_gregorian(date2)
    
    if d1 < d2:
        return -1
    elif d1 > d2:
        return 1
    else:
        return 0
