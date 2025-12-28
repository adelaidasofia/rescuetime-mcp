"""Pydantic models for RescueTime API responses."""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class DailySummary(BaseModel):
    """Daily summary from the Daily Summary Feed API."""

    date: str
    productivity_pulse: float
    very_productive_percentage: float
    productive_percentage: float
    neutral_percentage: float
    distracting_percentage: float
    very_distracting_percentage: float
    all_productive_percentage: float
    all_distracting_percentage: float
    total_hours: float
    very_productive_hours: float
    productive_hours: float
    neutral_hours: float
    distracting_hours: float
    very_distracting_hours: float
    all_productive_hours: float
    all_distracting_hours: float
    total_duration_formatted: str
    very_productive_duration_formatted: str
    productive_duration_formatted: str
    neutral_duration_formatted: str
    distracting_duration_formatted: str
    very_distracting_duration_formatted: str
    all_productive_duration_formatted: str
    all_distracting_duration_formatted: str


class AnalyticDataRow(BaseModel):
    """A single row from the Analytic Data API.

    The API returns arrays where:
    - Row 0: Rank (for ranked perspective)
    - Row 1: Time spent (seconds)
    - Row 2: Number of people (always 1 for personal)
    - Row 3: Activity/Category name
    - Row 4: Category (for activities) or blank
    - Row 5: Productivity score (-2 to 2)
    """

    rank: int
    time_seconds: int
    name: str
    category: Optional[str] = None
    productivity: int  # -2=very distracting, -1=distracting, 0=neutral, 1=productive, 2=very productive

    @property
    def time_hours(self) -> float:
        """Time in hours."""
        return self.time_seconds / 3600

    @property
    def time_minutes(self) -> float:
        """Time in minutes."""
        return self.time_seconds / 60

    @property
    def productivity_label(self) -> str:
        """Human-readable productivity label."""
        labels = {
            2: "Very Productive",
            1: "Productive",
            0: "Neutral",
            -1: "Distracting",
            -2: "Very Distracting",
        }
        return labels.get(self.productivity, "Unknown")


class HourlyData(BaseModel):
    """Hourly productivity data from interval perspective."""

    hour: int  # 0-23
    date: str
    time_seconds: int
    productivity: int

    @property
    def time_minutes(self) -> float:
        """Time in minutes."""
        return self.time_seconds / 60
