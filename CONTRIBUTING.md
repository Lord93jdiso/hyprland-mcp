# Contributing

Thanks for your interest in improving this MCP server!

## How to contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-improvement`)
3. Make your changes
4. Add or update tests / error handling
5. Run syntax checks: `python -c "import ast; ast.parse(open('mcp_server.py').read())"`
6. Submit a Pull Request with a clear description

## Code guidelines

- Keep error messages user-friendly
- Always reference the official Hyprland wiki (`https://wiki.hypr.land/`)
- Maintain backward compatibility for existing tool signatures
- Add validation for new inputs using `ConfigValidationError`
