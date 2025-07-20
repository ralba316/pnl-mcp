import asyncio
import typer

from .server import run_sse, run_stdio

app = typer.Typer(help="PnL Analysis MCP Server")

@app.command()
def sse():
    """Start PnL Analysis MCP Server in SSE mode"""
    print("PnL Analysis MCP Server - SSE mode")
    print("-----------------------------------")
    print("Press Ctrl+C to exit")
    try:
        asyncio.run(run_sse())
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Service stopped.")

@app.command()
def stdio():
    """Start PnL Analysis MCP Server in stdio mode"""
    try:
        run_stdio()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Service stopped.")

if __name__ == "__main__":
    app()