import typer
import os
import json
from datetime import datetime
from collections import Counter
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.live import Live
from sqlite_utils import Database
import subprocess

app = typer.Typer(help="DevLog: A minimalist developer journaling CLI 🦞")
console = Console()

# Standard Statuses
STATUS_PENDING = "pending"
STATUS_COMPLETED = "completed"
STATUS_IN_PROGRESS = "in-progress"
STATUS_NONE = "none"
STANDARD_STATUSES = [STATUS_PENDING, STATUS_COMPLETED, STATUS_IN_PROGRESS, STATUS_NONE]

# Default DB path
DB_PATH = os.environ.get("DEVLOG_DB", os.path.expanduser("~/.devlog.db"))

def get_db():
    db = Database(DB_PATH)
    if "logs" not in db.table_names():
        db["logs"].create({
            "id": int,
            "content": str,
            "timestamp": str,
            "tags": str,
            "project": str,
            "status": str
        }, pk="id")
        db["logs"].enable_fts(["content", "tags", "project", "status"], create_triggers=True)
    else:
        # Schema migration for existing table
        columns = db["logs"].columns_dict
        if "project" not in columns:
            db["logs"].add_column("project", str)
        if "status" not in columns:
            db["logs"].add_column("status", str)
        
        # Ensure FTS covers new columns (re-enable if needed or just assume it might need update)
        # For sqlite-utils, we can just re-enable to update triggers
        db["logs"].enable_fts(["content", "tags", "project", "status"], create_triggers=True, replace=True)
        
    return db

@app.command()
def add(
    content: str = typer.Argument(None, help="Log content (optional, triggers interactive mode if omitted)"),
    tags: str = typer.Option("", help="Comma-separated tags"),
    project: str = typer.Option("", help="Project name"),
    status: str = typer.Option(None, help="Status (pending, completed, in-progress, none or custom)")
):
    """
    Add a new log entry. Interactive mode if content is missing.
    """
    if content is None:
        console.print("[bold cyan]Interactive Mode[/bold cyan]")
        content = Prompt.ask("📝 Log entry")
        if not tags:
            tags = Prompt.ask("🏷️  Tags (comma separated)", default="")
        if not project:
            project = Prompt.ask("📂 Project", default="")
        if status is None:
            status = Prompt.ask("📊 Status", choices=STANDARD_STATUSES + ["custom"], default=STATUS_NONE)
            if status == "custom":
                status = Prompt.ask("   Enter custom status")
    
    if status is None:
        status = STATUS_NONE

    db = get_db()
    db["logs"].insert({
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "tags": tags,
        "project": project,
        "status": status
    })
    console.print(f"[bold green]✓ Log saved![/bold green] (Project: {project}, Status: {status})")

@app.command()
def view(id: int = typer.Argument(..., help="ID of the log entry to view")):
    """
    Display a single log entry in a beautiful, full-width view.
    """
    db = get_db()
    try:
        row = db["logs"].get(id)
    except Exception:
        console.print(f"[red]Log entry with ID {id} not found.[/red]")
        return

    dt = datetime.fromisoformat(row["timestamp"])
    
    header = f"[bold cyan]ID:[/bold cyan] {row['id']} | [bold cyan]Time:[/bold cyan] {dt.strftime('%Y-%m-%d %H:%M:%S')}"
    meta = f"[bold magenta]Project:[/bold magenta] {row.get('project') or 'N/A'} | [bold green]Status:[/bold green] {row.get('status') or 'N/A'} | [bold yellow]Tags:[/bold yellow] {row.get('tags') or 'N/A'}"
    
    panel = Panel(
        Markdown(row["content"]),
        title=header,
        subtitle=meta,
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)

@app.command()
def edit(id: int = typer.Argument(..., help="ID of the log entry to edit")):
    """
    Interactively edit a log entry.
    """
    db = get_db()
    try:
        row = db["logs"].get(id)
    except Exception:
        console.print(f"[red]Log entry with ID {id} not found.[/red]")
        return

    console.print(f"[bold cyan]Editing Log Entry #{id}[/bold cyan]")
    
    new_content = Prompt.ask("📝 Content", default=row["content"])
    new_project = Prompt.ask("📂 Project", default=row.get("project", ""))
    
    current_status = row.get("status", STATUS_NONE)
    status_choices = STANDARD_STATUSES + ["custom"]
    if current_status not in STANDARD_STATUSES:
        status_choices.append(current_status)
        
    new_status = Prompt.ask("📊 Status", choices=status_choices, default=current_status)
    if new_status == "custom":
        new_status = Prompt.ask("   Enter custom status")
        
    new_tags = Prompt.ask("🏷️  Tags", default=row.get("tags", ""))

    db["logs"].update(id, {
        "content": new_content,
        "project": new_project,
        "status": new_status,
        "tags": new_tags
    })
    console.print(f"[bold green]✓ Log #{id} updated![/bold green]")

@app.command()
def delete(id: int = typer.Argument(..., help="ID of the log entry to delete")):
    """
    Delete a log entry with confirmation.
    """
    db = get_db()
    try:
        row = db["logs"].get(id)
    except Exception:
        console.print(f"[red]Log entry with ID {id} not found.[/red]")
        return

    # Show entry before deleting
    dt = datetime.fromisoformat(row["timestamp"])
    console.print(f"[yellow]Are you sure you want to delete this log entry?[/yellow]")
    console.print(f"ID: {row['id']} | Time: {dt.strftime('%Y-%m-%d %H:%M')} | Content: {row['content'][:50]}...")
    
    if Confirm.ask("Delete?"):
        db["logs"].delete(id)
        console.print(f"[bold red]✓ Log #{id} deleted.[/bold red]")
    else:
        console.print("Deletion cancelled.")

@app.command(name="list")
def list_logs(
    limit: int = typer.Option(10, help="Number of logs to show"),
    tag: str = typer.Option(None, help="Filter by tag"),
    grep: str = typer.Option(None, help="Filter by content (simple grep)"),
    project: str = typer.Option(None, help="Filter by project"),
    status: str = typer.Option(None, help="Filter by status")
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

    if project:
        where_clauses.append("project = ?")
        args.append(project)

    if status:
        where_clauses.append("status = ?")
        args.append(status)
        
    where = " AND ".join(where_clauses) if where_clauses else None
    
    try:
        rows = list(db["logs"].rows_where(where, args, order_by="timestamp desc", limit=limit))
    except Exception as e:
        console.print(f"[red]Error fetching logs: {e}[/red]")
        return
    
    if not rows:
        console.print("[yellow]No logs found.[/yellow]")
        return

    table = Table(title=f"Dev Logs (Last {len(rows)})", border_style="blue", expand=True)
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Time", style="cyan", no_wrap=True)
    table.add_column("Project", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Content", style="white")
    table.add_column("Tags", style="yellow")

    status_counts = Counter()
    for row in rows:
        dt = datetime.fromisoformat(row["timestamp"])
        status_counts[row.get("status") or "none"] += 1
        
        # Truncate long content for list view
        content_preview = row["content"].split('\n')[0]
        if len(content_preview) > 50:
            content_preview = content_preview[:47] + "..."
            
        table.add_row(
            str(row["id"]),
            dt.strftime("%Y-%m-%d %H:%M"), 
            row.get("project", ""), 
            row.get("status", ""), 
            content_preview, 
            row.get("tags", "")
        )
    
    console.print(table)
    
    # Status Summary
    summary_parts = [f"[bold]{s}:[/bold] {c}" for s, c in status_counts.items()]
    console.print(Panel(" | ".join(summary_parts), title="Status Summary", border_style="dim"))

@app.command(name="ls")
def ls_alias(
    limit: int = typer.Option(10, help="Number of logs to show"),
    tag: str = typer.Option(None, help="Filter by tag"),
    grep: str = typer.Option(None, help="Filter by content (simple grep)"),
    project: str = typer.Option(None, help="Filter by project"),
    status: str = typer.Option(None, help="Filter by status")
):
    """Alias for list"""
    list_logs(limit=limit, tag=tag, grep=grep, project=project, status=status)

@app.command()
def search(query: str):
    """
    Search logs using full-text search with a fallback to LIKE.
    """
    db = get_db()
    results = []
    
    # Try FTS first
    try:
        results = list(db["logs"].search(query))
    except Exception:
        pass
        
    # If no FTS results, try case-insensitive LIKE
    if not results:
        results = list(db["logs"].rows_where(
            "content LIKE ? OR tags LIKE ?", 
            [f"%{query}%", f"%{query}%"],
            order_by="timestamp desc"
        ))
    
    if not results:
        console.print("[red]No matches found.[/red]")
        return
        
    console.print(f"[bold green]Found {len(results)} matches for '[italic]{query}[/italic]':[/bold green]")
    for row in results:
        dt = datetime.fromisoformat(row["timestamp"])
        
        # Enhanced result display
        header = f"[bold cyan]ID:[/bold cyan] {row['id']} | [bold cyan]{dt.strftime('%Y-%m-%d %H:%M')}[/bold cyan]"
        meta = f"[bold magenta]Project:[/bold magenta] {row.get('project') or 'N/A'} | [bold green]Status:[/bold green] {row.get('status') or 'N/A'} | [bold yellow]Tags:[/bold yellow] {row.get('tags') or 'N/A'}"
        
        panel = Panel(
            Markdown(row["content"]),
            title=header,
            subtitle=meta,
            border_style="green",
            padding=(0, 1)
        )
        console.print(panel)

@app.command()
def stats(
    project: str = typer.Option(None, help="Filter stats by project")
):
    """
    Show analytics and statistics.
    """
    db = get_db()
    
    where = "project = ?" if project else None
    args = [project] if project else []
    
    all_logs = list(db["logs"].rows_where(where, args))
    count = len(all_logs)
    
    if count == 0:
        console.print(f"No logs found{f' for project {project}' if project else ''}.")
        return

    title_suffix = f" (Project: {project})" if project else ""

    # Activity Heatmap (Last 30 days)
    from datetime import date, timedelta
    today = date.today()
    last_30_days = [today - timedelta(days=i) for i in range(30)]
    last_30_days.reverse()
    
    dates_in_logs = [datetime.fromisoformat(log["timestamp"]).date() for log in all_logs]
    activity_counts = Counter(dates_in_logs)
    
    heatmap_str = ""
    for d in last_30_days:
        c = activity_counts.get(d, 0)
        if c == 0:
            heatmap_str += "[grey37]□ [/grey37]"
        elif c < 3:
            heatmap_str += "[green]■ [/green]"
        elif c < 6:
            heatmap_str += "[bold green]■ [/bold green]"
        else:
            heatmap_str += "[bold bright_green]■ [/bold bright_green]"
    
    console.print(Panel(heatmap_str, title=f"Activity (Last 30 Days){title_suffix}", subtitle="□:0 ■:1-2 ■:3-5 ■:6+"))

    # Tag analysis
    all_tags = []
    for log in all_logs:
        if log.get("tags"):
            tags = [t.strip() for t in log["tags"].split(",") if t.strip()]
            all_tags.extend(tags)
    
    tag_counts = Counter(all_tags).most_common(5)
    
    # Time analysis (logs per day)
    date_counts = Counter(dates_in_logs).most_common(5)

    console.print(Panel(f"[bold white]Total Entries:[/bold white] [bold green]{count}[/bold green]", title=f"General Stats{title_suffix}"))
    
    tag_table = Table(title=f"Top Tags{title_suffix}", show_header=True)
    tag_table.add_column("Tag", style="yellow")
    tag_table.add_column("Count", style="white")
    for tag, c in tag_counts:
        tag_table.add_row(tag, str(c))
    
    console.print(tag_table)

@app.command()
def sync(
    repo: str = typer.Option(None, help="Git repo URL to sync with"),
    path: str = typer.Option(None, help="Local backup path")
):
    """
    Sync/Backup ~/.devlog.db to a private git repo or local path.
    """
    if not repo and not path:
        action = Prompt.ask("Sync to", choices=["git", "local"], default="local")
        if action == "git":
            repo = Prompt.ask("Git Repo URL")
        else:
            path = Prompt.ask("Local Backup Path", default="~/devlog_backup")

    import shutil
    db_source = DB_PATH
    
    if path:
        path = os.path.expanduser(path)
        os.makedirs(path, exist_ok=True)
        dest = os.path.join(path, "devlog.db")
        shutil.copy2(db_source, dest)
        console.print(f"[bold green]✓ Backed up to {dest}[/bold green]")
    
    if repo:
        sync_dir = os.path.expanduser("~/.devlog_sync")
        if not os.path.exists(sync_dir):
            os.makedirs(sync_dir)
            subprocess.run(["git", "init"], cwd=sync_dir)
            if repo:
                subprocess.run(["git", "remote", "add", "origin", repo], cwd=sync_dir)
        
        shutil.copy2(db_source, os.path.join(sync_dir, "devlog.db"))
        subprocess.run(["git", "add", "devlog.db"], cwd=sync_dir)
        subprocess.run(["git", "commit", "-m", f"Sync: {datetime.now().isoformat()}"], cwd=sync_dir)
        
        result = subprocess.run(["git", "push", "origin", "main"], cwd=sync_dir, capture_output=True, text=True)
        if result.returncode == 0:
            console.print("[bold green]✓ Synced to Git![/bold green]")
        else:
            console.print(f"[red]Git push failed: {result.stderr}[/red]")

@app.command()
def export(
    format: str = typer.Option(None, help="Format: markdown or json"),
    output: str = typer.Option(None, help="Output file path")
):
    """
    Export logs to Markdown or JSON (Interactive).
    """
    # Interactive Format
    if not format:
        format = Prompt.ask("📂 Choose format", choices=["markdown", "json"], default="markdown")
    
    # Interactive Output Filename
    if not output:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = "md" if format == "markdown" else "json"
        default_filename = f"devlog_export_{now}.{ext}"
        
        output_name = Prompt.ask("📄 Filename", default=default_filename)
        output_path = Prompt.ask("📍 Path (folder)", default=".")
        output = os.path.join(output_path, output_name)

    db = get_db()
    logs = list(db["logs"].rows_where(order_by="timestamp desc"))
    
    if not logs:
        console.print("[yellow]Nothing to export.[/yellow]")
        return

    result = ""
    if format.lower() == "json":
        result = json.dumps(logs, indent=2)
    else:
        result += "# DevLog Export\n\n"
        for log in logs:
            dt = datetime.fromisoformat(log["timestamp"])
            result += f"## {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            if log.get("tags"):
                result += f"**Tags:** `{log['tags']}`\n\n"
            result += f"{log['content']}\n\n"
            result += "---\n\n"
            
    try:
        with open(output, "w") as f:
            f.write(result)
        console.print(f"[bold green]✓ Exported to {output}[/bold green]")
    except Exception as e:
        console.print(f"[red]Failed to export: {e}[/red]")

if __name__ == "__main__":
    app()
