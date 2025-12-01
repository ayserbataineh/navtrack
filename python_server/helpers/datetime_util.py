"""DateTime utilities for GPS message parsing."""

import re
from datetime import datetime
from typing import Optional

from ..models.enums import DateFormat


class DateTimeUtil:
    """Utility class for datetime operations."""
    
    @staticmethod
    def new(
        year: str,
        month: str,
        day: str,
        hour: str,
        minute: str,
        second: str,
        millisecond: Optional[str] = None,
        add_2000_year: bool = True
    ) -> datetime:
        """Create a new UTC datetime from string components."""
        year_int = int(year)
        if add_2000_year:
            year_int += 2000
        
        ms = int(millisecond) if millisecond else 0
        # Ensure millisecond is in microseconds (0-999999)
        if ms < 1000:
            ms *= 1000
        
        return datetime(
            year=year_int,
            month=int(month),
            day=int(day),
            hour=int(hour),
            minute=int(minute),
            second=int(second),
            microsecond=ms
        )
    
    @staticmethod
    def new_from_hex(
        year_hex: str,
        month_hex: str,
        day_hex: str,
        hour_hex: str,
        minute_hex: str,
        second_hex: str,
        millisecond_hex: Optional[str] = None,
        add_2000_year: bool = True
    ) -> datetime:
        """Create a new UTC datetime from hex string components."""
        year = int(year_hex, 16)
        month = int(month_hex, 16)
        day = int(day_hex, 16)
        hour = int(hour_hex, 16)
        minute = int(minute_hex, 16)
        second = int(second_hex, 16)
        millisecond = int(millisecond_hex, 16) if millisecond_hex else 0
        
        if add_2000_year:
            year += 2000
        
        # Ensure millisecond is in microseconds
        if millisecond < 1000:
            millisecond *= 1000
        
        return datetime(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            microsecond=millisecond
        )
    
    @staticmethod
    def convert(date_format: DateFormat, *inputs: str) -> datetime:
        """Convert input strings to datetime based on format."""
        if date_format == DateFormat.HHMMSS_SS_DDMMYY:
            return DateTimeUtil._parse_hhmmss_ss_ddmmyy(inputs)
        elif date_format == DateFormat.YYYYMMDDHHMMSS:
            return DateTimeUtil._parse_yyyymmddhhmmss(inputs)
        elif date_format == DateFormat.DDMMYYHHMMSS:
            return DateTimeUtil._parse_ddmmyyhhmmss(inputs)
        elif date_format == DateFormat.DDMMYY_HHMMSS:
            return DateTimeUtil._parse_ddmmyy_hhmmss(inputs)
        else:
            return DateTimeUtil._parse_yymmddhhmmss(inputs)
    
    @staticmethod
    def _parse_hhmmss_ss_ddmmyy(inputs: tuple) -> datetime:
        """Parse HHMMSS.SS,DDMMYY format."""
        time_match = re.match(r"(\d{2})(\d{2})(\d{2})\.(\d+)", inputs[0])
        date_match = re.match(r"(\d{2})(\d{2})(\d{2})", inputs[1])
        
        if not time_match or not date_match:
            raise ValueError(f"Invalid datetime format: {inputs}")
        
        return DateTimeUtil.new(
            date_match.group(3),  # year
            date_match.group(2),  # month
            date_match.group(1),  # day
            time_match.group(1),  # hour
            time_match.group(2),  # minute
            time_match.group(3),  # second
            time_match.group(4)   # millisecond
        )
    
    @staticmethod
    def _parse_yymmddhhmmss(inputs: tuple) -> datetime:
        """Parse YYMMDDHHMMSS format."""
        match = re.match(r"(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})", inputs[0])
        if not match:
            raise ValueError(f"Invalid datetime format: {inputs[0]}")
        
        return DateTimeUtil.new(
            match.group(1),  # year
            match.group(2),  # month
            match.group(3),  # day
            match.group(4),  # hour
            match.group(5),  # minute
            match.group(6)   # second
        )
    
    @staticmethod
    def _parse_yyyymmddhhmmss(inputs: tuple) -> datetime:
        """Parse YYYYMMDDHHMMSS format."""
        match = re.match(r"(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})", inputs[0])
        if not match:
            raise ValueError(f"Invalid datetime format: {inputs[0]}")
        
        return DateTimeUtil.new(
            match.group(1),  # year
            match.group(2),  # month
            match.group(3),  # day
            match.group(4),  # hour
            match.group(5),  # minute
            match.group(6),  # second
            add_2000_year=False
        )
    
    @staticmethod
    def _parse_ddmmyyhhmmss(inputs: tuple) -> datetime:
        """Parse DDMMYYHHMMSS format."""
        match = re.match(r"(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})", inputs[0])
        if not match:
            raise ValueError(f"Invalid datetime format: {inputs[0]}")
        
        return DateTimeUtil.new(
            match.group(3),  # year
            match.group(2),  # month
            match.group(1),  # day
            match.group(4),  # hour
            match.group(5),  # minute
            match.group(6)   # second
        )
    
    @staticmethod
    def _parse_ddmmyy_hhmmss(inputs: tuple) -> datetime:
        """Parse DD/MM/YY HH:MM:SS format."""
        date_match = re.match(r"(\d+)/(\d+)/(\d+)", inputs[0])
        time_match = re.match(r"(\d+):(\d+):(\d+)", inputs[1])
        
        if not date_match or not time_match:
            raise ValueError(f"Invalid datetime format: {inputs}")
        
        return DateTimeUtil.new(
            date_match.group(3),  # year
            date_match.group(2),  # month
            date_match.group(1),  # day
            time_match.group(1),  # hour
            time_match.group(2),  # minute
            time_match.group(3)   # second
        )
