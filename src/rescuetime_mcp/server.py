"""RescueTime MCP Server - Expose RescueTime productivity data to Claude."""

from datetime import date, timedelta

from fastmcp import FastMCP

from rescuetime_mcp.client import (
    RescueTimeClient,
    RescueTimeAuthError,
    RescueTimeAPIError,
)

mcp = FastMCP("RescueTime")


def format_hours_minutes(hours: float) -> str:
    """Format hours as 'Xh Ym'."""
    h = int(hours)
    m = int((hours - h) * 60)
    if h > 0:
        return f"{h}h {m}m"
    return f"{m}m"


def format_duration(seconds: int) -> str:
    """Format seconds as 'Xh Ym'."""
    return format_hours_minutes(seconds / 3600)


def productivity_bar(score: float, width: int = 10) -> str:
    """Create a visual bar for productivity score (0-100)."""
    filled = int(score * width / 100)
    return "\u2588" * filled + "\u2591" * (width - filled)


def resolve_date(date_str: str) -> str:
    """Resolve 'today', 'yesterday', or return as-is."""
    if date_str.lower() == "today":
        return date.today().isoformat()
    elif date_str.lower() == "yesterday":
        return (date.today() - timedelta(days=1)).isoformat()
    return date_str


@mcp.tool()
async def get_today_summary() -> str:
    """Get today's complete RescueTime productivity summary.

    This is the recommended daily check-in tool. Returns:
    - Productivity pulse (0-100 score)
    - Total time logged
    - Time breakdown by productivity level
    - Productive vs distracting percentages
    """
    try:
        client = RescueTimeClient()
        summaries = await client.get_daily_summary()

        if not summaries:
            return "No data available yet for today."

        today = summaries[0]
        lines = ["=== RescueTime Daily Summary ===", f"Date: {today.date}", ""]

        # Productivity pulse
        pulse = today.productivity_pulse
        lines.append("PRODUCTIVITY PULSE")
        lines.append(f"  {productivity_bar(pulse)} {pulse:.0f}/100")
        lines.append("")

        # Time summary
        lines.append("TIME LOGGED")
        lines.append(f"  Total: {today.total_duration_formatted}")
        lines.append(f"  Productive: {today.all_productive_duration_formatted} ({today.all_productive_percentage:.0f}%)")
        lines.append(f"  Distracting: {today.all_distracting_duration_formatted} ({today.all_distracting_percentage:.0f}%)")
        lines.append("")

        # Breakdown
        lines.append("BREAKDOWN")
        lines.append(f"  Very Productive: {today.very_productive_duration_formatted}")
        lines.append(f"  Productive:      {today.productive_duration_formatted}")
        lines.append(f"  Neutral:         {today.neutral_duration_formatted}")
        lines.append(f"  Distracting:     {today.distracting_duration_formatted}")
        lines.append(f"  Very Distracting:{today.very_distracting_duration_formatted}")

        return "\n".join(lines)

    except RescueTimeAuthError as e:
        return f"Authentication error: {e}"
    except RescueTimeAPIError as e:
        return f"API error: {e}"


@mcp.tool()
async def get_productivity_trend(days: int = 7) -> str:
    """Get productivity pulse trend for the last N days.

    Args:
        days: Number of days to look back (default: 7, max 14)

    Shows the daily productivity pulse with visual bars and calculates averages.
    Useful for identifying patterns and trends over time.
    """
    try:
        client = RescueTimeClient()
        summaries = await client.get_daily_summary()

        if not summaries:
            return "No productivity data available."

        # Limit to requested days
        summaries = summaries[:min(days, len(summaries))]

        lines = [f"Productivity Trend (last {len(summaries)} days):", ""]

        for day in summaries:
            pulse = day.productivity_pulse
            bar = productivity_bar(pulse)
            date_short = day.date[5:]  # MM-DD
            lines.append(f"{date_short}: {bar} {pulse:.0f} ({day.total_duration_formatted})")

        # Calculate averages
        if summaries:
            avg_pulse = sum(d.productivity_pulse for d in summaries) / len(summaries)
            avg_productive = sum(d.all_productive_percentage for d in summaries) / len(summaries)
            total_hours = sum(d.total_hours for d in summaries)
            lines.append("")
            lines.append(f"Average: {avg_pulse:.0f} pulse, {avg_productive:.0f}% productive")
            lines.append(f"Total logged: {format_hours_minutes(total_hours)}")

        return "\n".join(lines)

    except RescueTimeAuthError as e:
        return f"Authentication error: {e}"
    except RescueTimeAPIError as e:
        return f"API error: {e}"


@mcp.tool()
async def get_activity_data(date_str: str = "today", limit: int = 10) -> str:
    """Get top activities/applications by time spent.

    Args:
        date_str: Date to query - 'today', 'yesterday', or 'YYYY-MM-DD'
        limit: Maximum number of activities to show (default: 10)

    Shows which specific applications and websites you spent time on,
    ranked by duration. Includes productivity classification for each.
    """
    try:
        client = RescueTimeClient()
        resolved_date = resolve_date(date_str)

        activities = await client.get_analytic_data(
            restrict_kind="activity",
            perspective="rank",
            restrict_begin=resolved_date,
            restrict_end=resolved_date,
        )

        if not activities:
            return f"No activity data for {resolved_date}."

        lines = [f"Top Activities ({resolved_date}):", ""]

        for i, act in enumerate(activities[:limit], 1):
            prod_indicator = {
                2: "[++]",
                1: "[+ ]",
                0: "[  ]",
                -1: "[ -]",
                -2: "[--]",
            }.get(act.productivity, "[??]")

            duration = format_duration(act.time_seconds)
            lines.append(f"{i:2}. {prod_indicator} {act.name}")
            lines.append(f"      {duration} | {act.category or 'Uncategorized'}")

        # Show totals
        total_seconds = sum(a.time_seconds for a in activities)
        lines.append("")
        lines.append(f"Total: {format_duration(total_seconds)} across {len(activities)} activities")

        return "\n".join(lines)

    except RescueTimeAuthError as e:
        return f"Authentication error: {e}"
    except RescueTimeAPIError as e:
        return f"API error: {e}"


@mcp.tool()
async def get_category_breakdown(date_str: str = "today") -> str:
    """Get time spent by category.

    Args:
        date_str: Date to query - 'today', 'yesterday', or 'YYYY-MM-DD'

    Shows high-level categories like Software Development, Communication,
    Reference & Learning, etc. with time and productivity classification.
    """
    try:
        client = RescueTimeClient()
        resolved_date = resolve_date(date_str)

        categories = await client.get_analytic_data(
            restrict_kind="category",
            perspective="rank",
            restrict_begin=resolved_date,
            restrict_end=resolved_date,
        )

        if not categories:
            return f"No category data for {resolved_date}."

        lines = [f"Category Breakdown ({resolved_date}):", ""]

        total_seconds = sum(c.time_seconds for c in categories)

        for cat in categories:
            duration = format_duration(cat.time_seconds)
            percentage = (cat.time_seconds / total_seconds * 100) if total_seconds > 0 else 0
            prod_label = cat.productivity_label

            # Visual bar based on percentage
            bar_len = int(percentage / 5)
            bar = "\u2588" * bar_len

            lines.append(f"{cat.name}")
            lines.append(f"  {bar} {duration} ({percentage:.0f}%) - {prod_label}")

        lines.append("")
        lines.append(f"Total: {format_duration(total_seconds)}")

        return "\n".join(lines)

    except RescueTimeAuthError as e:
        return f"Authentication error: {e}"
    except RescueTimeAPIError as e:
        return f"API error: {e}"


@mcp.tool()
async def get_hourly_productivity(date_str: str = "today") -> str:
    """Get productivity breakdown by hour.

    Args:
        date_str: Date to query - 'today', 'yesterday', or 'YYYY-MM-DD'

    Shows when during the day you were most/least productive.
    Useful for identifying peak productivity hours and scheduling deep work.
    """
    try:
        client = RescueTimeClient()
        resolved_date = resolve_date(date_str)

        hourly = await client.get_hourly_data(
            restrict_begin=resolved_date,
            restrict_end=resolved_date,
        )

        if not hourly:
            return f"No hourly data for {resolved_date}."

        lines = [f"Hourly Productivity ({resolved_date}):", ""]

        # Group by hour and find the peak
        hour_data = {}
        for h in hourly:
            if h.hour not in hour_data:
                hour_data[h.hour] = {"seconds": 0, "productivity_sum": 0, "count": 0}
            hour_data[h.hour]["seconds"] += h.time_seconds
            hour_data[h.hour]["productivity_sum"] += h.productivity * h.time_seconds
            hour_data[h.hour]["count"] += 1

        if not hour_data:
            return f"No hourly data for {resolved_date}."

        # Display each hour
        for hour in sorted(hour_data.keys()):
            data = hour_data[hour]
            mins = data["seconds"] / 60
            if mins < 1:
                continue

            # Weighted average productivity
            avg_prod = data["productivity_sum"] / data["seconds"] if data["seconds"] > 0 else 0

            # Visual representation
            bar_len = min(int(mins / 6), 10)  # 60 mins = 10 blocks
            bar = "\u2588" * bar_len + "\u2591" * (10 - bar_len)

            # Productivity indicator
            prod_char = {
                2: "++", 1: "+ ", 0: "  ", -1: " -", -2: "--"
            }.get(round(avg_prod), "  ")

            hour_str = f"{hour:02d}:00"
            lines.append(f"{hour_str} [{prod_char}] {bar} {mins:.0f}m")

        # Summary
        total_mins = sum(d["seconds"] for d in hour_data.values()) / 60
        if hour_data:
            peak_hour = max(hour_data.keys(), key=lambda h: hour_data[h]["seconds"])
            lines.append("")
            lines.append(f"Peak hour: {peak_hour:02d}:00 ({hour_data[peak_hour]['seconds']/60:.0f}m)")
            lines.append(f"Total: {total_mins:.0f} minutes logged")

        return "\n".join(lines)

    except RescueTimeAuthError as e:
        return f"Authentication error: {e}"
    except RescueTimeAPIError as e:
        return f"API error: {e}"


def main():
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
