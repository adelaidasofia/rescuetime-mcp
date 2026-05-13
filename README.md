# RescueTime MCP Server

A lightweight [MCP](https://modelcontextprotocol.io/) server that gives Claude access to your [RescueTime](https://www.rescuetime.com/) productivity data. Built with [FastMCP](https://gofastmcp.com/).

## Tools

| Tool | Description |
|------|-------------|
| `get_daily_summary` | Productivity pulse, hours logged, productive vs. distracting time breakdown |
| `get_top_activities` | Top apps/websites ranked by time spent |
| `get_categories` | Time breakdown by category (Development, Communication, Social, etc.) |
| `get_productivity_trend` | Productivity pulse trend over the past N days |

All tools accept a `day` parameter: `"today"`, `"yesterday"`, or `"YYYY-MM-DD"`.

## Install

Open Claude Code, paste:

    /plugin marketplace add adelaidasofia/rescuetime-mcp
    /plugin install rescuetime-mcp@rescuetime-mcp

Then get a RescueTime API key at [rescuetime.com/anapi/manage](https://www.rescuetime.com/anapi/manage) and set `RESCUETIME_API_KEY` in your environment.

<details>
<summary>Legacy install</summary>

### 1. Get your API key

Go to [rescuetime.com/anapi/manage](https://www.rescuetime.com/anapi/manage) and create or copy an API key.

### 2. Install FastMCP

```bash
pipx install fastmcp
```

Or with `uv`:

```bash
uv tool install fastmcp
```

### 3. Add to Claude Code

```bash
claude mcp add rescuetime \
  -e RESCUETIME_API_KEY=your_api_key_here \
  -- fastmcp run /path/to/server.py
```

Or add manually to your `.mcp.json`:

```json
{
  "mcpServers": {
    "rescuetime": {
      "command": "fastmcp",
      "args": ["run", "/path/to/server.py"],
      "env": {
        "RESCUETIME_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### 4. Restart Claude Code

The RescueTime tools should appear in your session.

</details>

## Example Usage

Once connected, you can ask Claude things like:

- "How productive was I today?"
- "What apps did I spend the most time on yesterday?"
- "Show me my productivity trend for the last 7 days"
- "What categories did I spend time on this week?"

## Requirements

- Python 3.11+
- [FastMCP](https://gofastmcp.com/) 3.x
- A RescueTime account (free or premium)
- RescueTime API key

## How It Works

The server calls the [RescueTime Analytic Data API](https://www.rescuetime.com/apidoc) using your API key and returns structured productivity data that Claude can reason about. No data is stored or sent anywhere except back to your Claude session.

## Related MCPs

Same author, same architecture pattern (FastMCP, draft+confirm on writes where applicable, vault auto-export, MIT):

- [slack-mcp](https://github.com/adelaidasofia/slack-mcp) — multi-workspace Slack
- [imessage-mcp](https://github.com/adelaidasofia/imessage-mcp) — macOS iMessage
- [whatsapp-mcp](https://github.com/adelaidasofia/whatsapp-mcp) — WhatsApp via whatsmeow
- [google-workspace-mcp](https://github.com/adelaidasofia/google-workspace-mcp) — Gmail / Calendar / Drive / Docs / Sheets
- [apollo-mcp](https://github.com/adelaidasofia/apollo-mcp) — Apollo.io CRM + sequences
- [substack-mcp](https://github.com/adelaidasofia/substack-mcp) — Substack writing + analytics
- [luma-mcp](https://github.com/adelaidasofia/luma-mcp) — lu.ma events
- [parse-mcp](https://github.com/adelaidasofia/parse-mcp) — markitdown / Docling / LlamaParse router
- [graph-query-mcp](https://github.com/adelaidasofia/graph-query-mcp) — vault knowledge graph queries
- [graph-autotagger-mcp](https://github.com/adelaidasofia/graph-autotagger-mcp) — wikilink suggestions from the graph
- [investor-relations-mcp](https://github.com/adelaidasofia/investor-relations-mcp) — seed-raise pipeline tracker
- [vault-sync-mcp](https://github.com/adelaidasofia/vault-sync-mcp) — bidirectional vault sync


## Telemetry

This plugin sends a single anonymous install signal to `myceliumai.co` the first time it loads in a Claude Code session on a given machine.

**What is sent:**
- Plugin name (e.g. `slack-mcp`)
- Plugin version (e.g. `0.1.0`)

**What is NOT sent:**
- No user identifiers, names, emails, tokens, or API keys
- No file paths, message content, or anything from your work
- No IP address is stored after dedup processing

**Why:** Helps the maintainer know which plugins people actually install, so attention goes to the ones that get used.

**Opt out:** Set the environment variable `MYCELIUM_NO_PING=1` before launching Claude Code. The hook will skip the network call entirely. Already-pinged installs leave a sentinel at `~/.mycelium/onboarded-<plugin>` — delete it if you want to reset state.

## License

MIT

---

Built by Adelaida Diaz-Roa. Full install or team version at [diazroa.com](https://diazroa.com).
