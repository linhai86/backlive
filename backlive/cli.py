from datetime import date, datetime, timedelta

import click

from backlive.bootstrap import bootstrap
from backlive.domain.commands import DownloadCandleCommand, RunBacktestCommand
from backlive.infrastructure.database.database_initializer import DatabaseInitializer


@click.group()
@click.option("--debug/--no-debug", default=False, show_default=True, help="Enable debug mode.")
@click.pass_context
def cli(ctx: click.Context, debug: bool) -> None:
    """BackLive CLI."""
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug
    if debug:
        click.echo("Debug mode is on.")


@cli.command()
@click.option("--url", default="sqlite:///tickers.db", show_default=True, help="Database URL.")
@click.pass_context
def init(ctx: click.Context, url: str) -> None:
    """Initialize the database."""
    if ctx.obj["DEBUG"]:
        click.echo(f"Initializing database at {url}")

    db_initializer = DatabaseInitializer(url)
    db_initializer.initialize_database()
    click.echo("Database initialized successfully.")


@cli.command()
@click.option("--url", default="sqlite:///tickers.db", show_default=True, help="Database URL.")
@click.option("--symbol", required=True, help="Stock symbol (e.g., AAPL).")
@click.option(
    "--start",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=str(date.today() - timedelta(days=365)),
    show_default=True,
    help="Start date (YYYY-MM-DD).",
)
@click.option(
    "--end",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=str(date.today()),
    show_default=True,
    help="End date (YYYY-MM-DD).",
)
@click.option("--limit", type=int, default=1000, show_default=True, help="Number of records to fetch.")
@click.option("--interval", default="1d", show_default=True, help="Interval between data points (e.g., 1d, 1h).")
@click.pass_context
def fetch(ctx: click.Context, url: str, symbol: str, start: datetime, end: datetime, limit: int, interval: str) -> None:
    """Fetch data and save to the database."""
    if ctx.obj["DEBUG"]:
        click.echo(f"Fetching data for {symbol} from {start} to {end} with interval {interval}")

    message_bus = bootstrap(url)
    message_bus.handle(DownloadCandleCommand(symbol=symbol, start=start, end=end, interval=interval, limit=limit))


@cli.command()
@click.option("--url", default="sqlite:///tickers.db", show_default=True, help="Database URL.")
@click.option("--symbol", required=True, help="Stock symbol (e.g., AAPL).")
@click.option(
    "--start",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=str(date.today() - timedelta(days=365)),
    show_default=True,
    help="Start date (YYYY-MM-DD).",
)
@click.option(
    "--end",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=str(date.today()),
    show_default=True,
    help="End date (YYYY-MM-DD).",
)
@click.pass_context
def backtest(ctx: click.Context, url: str, symbol: str, start: datetime, end: datetime) -> None:
    """Backtest."""
    if ctx.obj["DEBUG"]:
        click.echo(f"Backtest {symbol}")

    message_bus = bootstrap(url)
    message_bus.handle(RunBacktestCommand(symbol=symbol, start=start, end=end))


if __name__ == "__main__":
    cli()
