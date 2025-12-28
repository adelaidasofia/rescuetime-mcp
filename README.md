# RescueTime MCP Server

An MCP (Model Context Protocol) server that provides Claude Desktop with access to your RescueTime productivity data, including daily summaries, activity tracking, and productivity trends.

## Features

- **Daily Summary**: Get your productivity pulse, time logged, and productive vs distracting breakdown
- **Productivity Trends**: Track your productivity score over the past week or more
- **Activity Data**: See which applications and websites you spent time on
- **Category Breakdown**: View time by category (Development, Communication, etc.)
- **Hourly Analysis**: Identify your peak productivity hours

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- A RescueTime account (free or premium)
- RescueTime API key

## Setup

### 1. Clone and Install

```bash
git clone https://github.com/JasonBates/rescuetime-mcp.git
cd rescuetime-mcp
uv sync
```

### 2. Get Your API Key

1. Go to [rescuetime.com/anapi/manage](https://www.rescuetime.com/anapi/manage)
2. Sign in with your RescueTime account
3. Create a new API key or copy an existing one

### 3. Configure Claude Desktop

Add the server to your Claude Desktop config at:
`~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "rescuetime": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/YOUR_USERNAME/Projects/rescuetime-mcp",
        "run",
        "rescuetime-mcp"
      ],
      "env": {
        "RESCUETIME_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Replace `YOUR_USERNAME` with your actual username and add your API key.

### 4. Restart Claude Desktop

Quit and reopen Claude Desktop. You should see "rescuetime" in the MCP servers list.

## Usage

Once configured, you can ask Claude things like:

- "How productive was I today?"
- "Show me my productivity trend for the past week"
- "What apps did I use most today?"
- "What categories did I spend time on yesterday?"
- "When was I most productive today?"

## Available Tools

| Tool | Description |
|------|-------------|
| `get_today_summary` | Today's productivity pulse, time logged, and breakdown |
| `get_productivity_trend` | Productivity score history (default 7 days) |
| `get_activity_data` | Top applications/websites by time spent |
| `get_category_breakdown` | Time spent by category |
| `get_hourly_productivity` | Productivity breakdown by hour |

## Tool Details

### get_today_summary
Returns a complete daily overview including:
- Productivity pulse (0-100 score)
- Total time logged
- Productive vs distracting percentages
- Breakdown by productivity level (very productive → very distracting)

### get_productivity_trend
Shows daily productivity pulse with visual bars over multiple days. Useful for identifying patterns and weekly trends.

### get_activity_data
Lists specific applications and websites ranked by time spent. Each activity shows:
- Productivity classification ([++] to [--])
- Duration
- Category

### get_category_breakdown
Groups time by high-level categories like Software Development, Communication, Reference & Learning, Social Networking, etc.

### get_hourly_productivity
Reveals when during the day you were most/least productive. Helps identify peak hours for scheduling deep work.

## Troubleshooting

### "Authentication error"
Make sure your API key is correctly set in the Claude Desktop config's `env` section.

### No data showing
RescueTime needs to be running and logging data on your devices. Check that the RescueTime app is active.

### Rate limiting
The RescueTime API has rate limits. If you encounter errors, wait a few minutes before retrying.

## Development

```bash
# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Test with MCP Inspector
npx @modelcontextprotocol/inspector uv run rescuetime-mcp
```

## License

MIT
