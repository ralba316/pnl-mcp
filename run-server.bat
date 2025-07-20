@echo off
cd /d D:\Codebase\pnl-mcp-server
uv sync
uv run pnl-mcp-server stdio
