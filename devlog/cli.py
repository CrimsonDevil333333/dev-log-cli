import typer
import os
import json
from datetime import datetime
from collections import Counter
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.panel import Panel
from sqlite_utils import Database

app = typer.Typer(help="DevLog: A minimalist developer journaling CLI 🦞")
console = Console()

# Default DB path
DB_PATH = os.environ.get("DEVLOG_DB", os.path.expanduser("~/.devlog.db"))

def get_db():
    db = Database(DB_PATH)
    if "logs" not in db.table_names():
        db["logs"].create({
            "id": int,
            "content": str,
            "timestamp": str,
            "tags": str
        }, pk="id")
        db["logs"].enable_fts(["content", "tags"])
    return db

@app.command()
def add(
    content: str = typer.Argument(None, help="Log content (optional, triggers interactive mode if omitted)"),
    tags: str = typer.Option("", help="Comma-separated tags")
):
    """
    Add a new log entry. Interactive mode if content is missing.
    """
    if content is None:
        console.print("[bold cyan]Interactive Mode[/bold cyan]")
        content = Prompt.ask("📝 Log entry")
        if not tags:
            tags = Prompt.ask("🏷️  Tags (comma separated)", default="")

    db = get_db()
    db["logs"].insert({
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "tags": tags
    })
    console.print(f"[bold green]✓ Log saved![/bold green] (Tags: {tags})")

@app.command(name="list")
def list_logs(
    limit: int = typer.Option(10, help="Number of logs to show"),
    tag: str = typer.Option(None, help="Filter by tag"),
    grep: str = typer.Option(None, help="Filter by content (simple grep)")
):
    """
    List recent logs.
    """
    db = get_db()
    
    where_clauses = []
    args = []
    
    if tag:
        where_clauses.append("tags LIKE ?")
        args.append(f"%{tag}%")
    
    if grep:
        where_clauses.append("content LIKE ?")
        args.append(f"%{grep}%")
        
    where = " AND ".join(where_clauses) if where_clauses else None
    
    rows = list(db["logs"].rows_where(where, args, order_by="timestamp desc", limit=limit))
    
    if not rows:
        console.print("[yellow]No logs found.[/yellow]")
        return

    table = Table(title=f"Dev Logs (Last {len(rows)})", border_style="blue")
    table.add_column("Time", style="cyan", no_wrap=True)
    table.add_column("Content", style="white")
    table.add_column("Tags", style="yellow")

    for row in rows:
        dt = datetime.fromisoformat(row["timestamp"])
        # Truncate long content for list view
        content_preview = row["content"].split('\n')[0]
        if len(content_preview) > 50:
            content_preview = content_preview[:47] + "..."
            
        table.add_row(dt.strftime("%Y-%m-%d %H:%M"), content_preview, row["tags"])
    
    console.print(table)

@app.command(name="ls")
def ls_alias(
    limit: int = typer.Option(10, help="Number of logs to show"),
    tag: str = typer.Option(None, help="Filter by tag")
):
    """Alias for list"""
    list_logs(limit=limit, tag=tag)

@app.command()
def search(query: str):
    """
    Search logs using full-text search.
    """
    db = get_db()
    results = list(db["logs"].search(query))
    
    if not results:
        console.print("[red]No matches found.[/red]")
        return
        
    console.print(f"[bold]Found {len(results)} matches:[/bold]")
    for row in results:
        dt = datetime.fromisoformat(row["timestamp"])
        panel = Panel(
            Markdown(row["content"]),
            title=f"[cyan]{dt.strftime('%Y-%m-%d %H:%M')}[/cyan] | [yellow]{row.get('tags', '')}[/yellow]",
            border_style="green"
        )
        console.print(panel)

@app.command()
def stats():
    """
    Show analytics and statistics.
    """
    db = get_db()
    all_logs = list(db["logs"].rows)
    count = len(all_logs)
    
    if count == 0:
        console.print("No logs yet.")
        return

    # Tag analysis
    all_tags = []
    for log in all_logs:
        if log["tags"]:
            tags = [t.strip() for t in log["tags"].split(",") if t.strip()]
            all_tags.extend(tags)
    
    tag_counts = Counter(all_tags).most_common(5)
    
    # Time analysis (logs per day)
    dates = [datetime.fromisoformat(log["timestamp"]).date() for log in all_logs]
    date_counts = Counter(dates).most_common(5)

    console.print(Panel(f"[bold white]Total Entries:[/bold white] [bold green]{count}[/bold green]", title="General Stats"))
    
    tag_table = Table(title="Top Tags", show_header=True)
    tag_table.add_column("Tag", style="yellow")
    tag_table.add_column("Count", style="white")
    for tag, c in tag_counts:
        tag_table.add_row(tag, str(c))
    
    console.print(tag_table)

@app.command()
def export(
    format: str = typer.Option("markdown", help="Format: markdown or json"),
    output: str = typer.Option(None, help="Output file path (prints to stdout if omitted)")
):
    """
    Export logs to Markdown or JSON.
    """
    db = get_db()
    logs = list(db["logs"].rows_where(order_by="timestamp desc"))
    
    result = ""
    
    if format.lower() == "json":
        result = json.dumps(logs, indent=2)
    else:
        # Markdown format
        result += "# DevLog Export\n\n"
        for log in logs:
            dt = datetime.fromisoformat(log["timestamp"])
            result += f"## {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            if log["tags"]:
                result += f"**Tags:** `{log['tags']}`\n\n"
            result += f"{log['content']}\n\n"
            result += "---\n\n"
            
    if output:
        with open(output, "w") as f:
            f.write(result)
        console.print(f"[bold green]✓ Exported to {output}[/bold green]")
    else:
        print(result)

if __name__ == "__main__":
    app()
