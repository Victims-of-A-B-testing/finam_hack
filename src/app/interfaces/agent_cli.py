"""
CLI for interacting with LangGraph agent system
"""

import click

from src.app.agents import run_agent_workflow


@click.command()
@click.argument("query", type=str)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def main(query: str, verbose: bool) -> None:
    """
    Interact with the LangGraph agent system.

    QUERY: Your question or request in Russian (e.g., "Найди акции Газпром")

    Examples:
        agent-cli "Найди информацию об акциях Газпром"
        agent-cli "Найди акции Apple" --verbose
    """
    if verbose:
        click.echo(f"📝 Query: {query}\n")

    try:
        click.echo("🤔 Thinking...\n")
        result = run_agent_workflow(query)

        click.echo("🤖 Agent Response:")
        click.echo("=" * 70)
        click.echo(result)
        click.echo("=" * 70)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        raise click.Abort() from e


if __name__ == "__main__":
    main()
