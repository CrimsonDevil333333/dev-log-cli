import typer
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
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
def add(content: str, tags: str = typer.Option("", help="Comma-separated tags")):
    """
    Add a new log entry.
    """
    db = get_db()
    db["logs"].insert({
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "tags": tags
    })
    console.print(f"[bold green]✓ Log saved![/bold green] (Tags: {tags})")

@app.command()
def ls(limit: int = 10, tag: str = None):
    """
    List recent logs.
    """
    db = get_db()
    
    query = "logs"
    where = None
    args = []
    
    if tag:
        where = "tags LIKE ?"
        args = [f"%{tag}%"]
    
    rows = db[query].rows_where(where, args, order_by="timestamp desc", limit=limit)
    
    table = Table(title=f"Dev Logs (Last {limit})")
    table.add_column("Time", style="cyan", no_wrap=True)
    table.add_column("Content", style="white")
    table.add_column("Tags", style="yellow")

    for row in rows:
        dt = datetime.fromisoformat(row["timestamp"])
        table.add_row(dt.strftime("%Y-%m-%d %H:%M"), row["content"].split('\n')[0], row["tags"])
    
    console.print(table)

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
        console.print(f"[cyan]{dt.strftime('%Y-%m-%d %H:%M')}[/cyan] | [yellow]{row['tags']}[/yellow]")
        console.print(Markdown(row["content"]))
        console.print("[dim]---[/dim]")

@app.command()
def stats():
    """
    Show simple stats.
    """
    db = get_db()
    count = db["logs"].count
    console.print(f"Total entries: [bold]{count}[/bold]")

if __name__ == "__main__":
    app()
