# Mac Monitor

Electron app to view macOS CPU, memory, and network usage.

## Development

- Requirements: Node.js 18+
- Install dependencies:

```bash
npm install
```

- Start the app:

```bash
npm run dev
```

## Notes
- Uses `systeminformation` to read metrics.
- Network rates and totals are aggregated across interfaces.