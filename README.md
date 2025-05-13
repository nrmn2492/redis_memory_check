
# Redis Memory Usage Checker

This script connects to a Redis instance and checks memory usage based on the `used_memory_rss` or `used_memory`
versus the configured `maxmemory`. It calculates percentage usage and exits with status **OK**, **WARN**, or **CRITICAL** accordingly.

## Features

- Connects to a Redis server and fetches memory metrics
- Compares actual memory usage to the configured `maxmemory`
- Returns appropriate exit codes and messages for monitoring integration
- Supports authentication and ACL users
- Lightweight and easy to integrate into any environment

## Usage

```bash
redis_memory_check.py [options]

python3 redis_memory_check.py -s 192.168.1.256 -p 6379 -a default -P Password321 -w 80 -c 90

python3 redis_memory_check.py -s 192.168.1.256 -p 6379 -a default -P Password321 -w 80 -c 90 --debug

python3 redis_memory_check.py --info
```

### Options

| Option            | Description                                                   | Default        |
|-------------------|---------------------------------------------------------------|----------------|
| `-s`, `--server`  | Redis hostname or IP address                                  | `127.0.0.1`    |
| `-p`, `--port`    | Redis TCP port                                                | `6379`         |
| `-a`, `--username`| Redis ACL username (optional)                                 | `None`         |
| `-P`, `--password`| Redis password (if required)                                  | `None`         |
| `-w`, `--warn`    | Warning threshold as a percentage of `maxmemory` (e.g., `80`) | Required       |
| `-c`, `--critical`| Critical threshold as a percentage of `maxmemory` (e.g., `90`)| Required       |
| `--debug=yes`     | Enable debug output                                           | Disabled       |
| `--info`          | Show help and exit                                            |                |

## Expected Output Examples

- **OK:**

  ```
  OK: Redis memory usage is 18MB / 1957MB (0.94%)
  ```

- **Warning:**

  ```
  WARN: Redis memory usage is 1700MB / 1957MB (86.89%)
  ```

- **Critical:**

  ```
  CRITICAL: Redis memory usage is 1950MB / 1957MB (99.64%)
  ```

## Notes

Inspired by: [https://gist.github.com/samuel/989234](https://gist.github.com/samuel/989234)

---

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

**THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.** IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
