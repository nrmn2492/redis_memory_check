#!/usr/bin/env python3

import socket
import sys
from optparse import OptionParser

EXIT_OK = 0
EXIT_WARN = 1
EXIT_CRITICAL = 2

TIMEOUT = 2
DEBUG = False

def debug(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")

def print_info():
    print("""
Redis Memory Usage Checker
--------------------------

This script connects to a Redis instance and checks memory usage based on the `used_memory_rss` or `used_memory`
versus the configured `maxmemory`. It calculates percentage usage and exits with OK/WARN/CRITICAL accordingly.

Options:

  -s, --server       Redis hostname or IP address (default: 127.0.0.1)
  -p, --port         Redis TCP port (default: 6379)
  -a, --username     Redis ACL username (optional)
  -P, --password     Redis password (if required)
  -w, --warn         Warning threshold in percentage of maxmemory (e.g., 80)
  -c, --critical     Critical threshold in percentage of maxmemory (e.g., 90)
  --debug=yes        Enable debug output
  --info             Show this help and exit

Expected Output Examples:

  OK:
    OK: Redis memory usage is 18MB / 1957MB (0.94%)

  Warning:
    WARN: Redis memory usage is 1700MB / 1957MB (86.89%)

  Critical:
    CRITICAL: Redis memory usage is 1950MB / 1957MB (99.64%)

""")
    sys.exit(0)

def get_info(host, port, username=None, password=None):
    debug(f"Connecting to Redis at {host}:{port}")
    socket.setdefaulttimeout(TIMEOUT)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((host, port))
        debug("Connection established")
    except Exception as e:
        print(f"[ERROR] Could not connect: {e}")
        raise

    if password:
        debug(f"Sending AUTH (username={'yes' if username else 'no'})")
        if username:
            auth_cmd = f"*3\r\n$4\r\nAUTH\r\n${len(username)}\r\n{username}\r\n${len(password)}\r\n{password}\r\n"
        else:
            auth_cmd = f"*2\r\n$4\r\nAUTH\r\n${len(password)}\r\n{password}\r\n"
        s.send(auth_cmd.encode())
        auth_resp = s.recv(1024)
        debug(f"AUTH response: {auth_resp!r}")
        if not auth_resp.startswith(b'+OK'):
            s.close()
            raise Exception("AUTH failed")

    debug("Sending INFO command")
    s.send(b"*1\r\n$4\r\ninfo\r\n")
    buf = b""
    while True:
        chunk = s.recv(2048)
        if not chunk:
            break
        buf += chunk
        if b"\r\n\r\n" in buf:
            break

    s.close()
    decoded = buf.decode("utf-8", errors="ignore")
    debug("INFO output received")
    return dict(x.split(':', 1) for x in decoded.split('\r\n') if ':' in x)

def build_parser():
    parser = OptionParser()
    parser.add_option("-s", "--server", dest="server", default="127.0.0.1")
    parser.add_option("-p", "--port", dest="port", type="int", default=6379)
    parser.add_option("-w", "--warn", dest="warn_percent", type="int")
    parser.add_option("-c", "--critical", dest="crit_percent", type="int")
    parser.add_option("-a", "--username", dest="username", default=None)
    parser.add_option("-P", "--password", dest="password", default=None)
    parser.add_option("--debug", dest="debug", default="no", help="Enable debug output (yes/no)")
    parser.add_option("--info", action="store_true", dest="info", help="Show usage information and exit")
    return parser

def main():
    global DEBUG

    parser = build_parser()
    options, _args = parser.parse_args()

    if options.info:
        print_info()

    if options.debug.lower() in ["yes", "true", "1"]:
        DEBUG = True

    if options.warn_percent is None or options.crit_percent is None:
        parser.error("Warning and critical thresholds (percentage) are required")

    try:
        info = get_info(options.server, options.port, options.username, options.password)
    except Exception as e:
        print(f"CRITICAL: Error connecting or getting INFO from Redis {options.server}:{options.port}: {e}")
        sys.exit(EXIT_CRITICAL)

    try:
        used_memory = int(info.get("used_memory_rss") or info["used_memory"])
        max_memory = int(info.get("maxmemory", 0))
    except KeyError as e:
        print(f"CRITICAL: Missing memory metrics in Redis INFO: {e}")
        sys.exit(EXIT_CRITICAL)

    if max_memory == 0:
        print("CRITICAL: Redis maxmemory is 0 (not configured)")
        sys.exit(EXIT_CRITICAL)

    used_percent = (used_memory / max_memory) * 100
    used_mb = used_memory // (1024 * 1024)
    max_mb = max_memory // (1024 * 1024)

    debug(f"Memory usage: {used_mb}MB / {max_mb}MB ({used_percent:.2f}%)")

    if used_percent > options.crit_percent:
        print(f"CRITICAL: Redis memory usage is {used_mb}MB / {max_mb}MB ({used_percent:.2f}%)")
        sys.exit(EXIT_CRITICAL)
    elif used_percent > options.warn_percent:
        print(f"WARN: Redis memory usage is {used_mb}MB / {max_mb}MB ({used_percent:.2f}%)")
        sys.exit(EXIT_WARN)

    print(f"OK: Redis memory usage is {used_mb}MB / {max_mb}MB ({used_percent:.2f}%)")
    sys.exit(EXIT_OK)

if __name__ == "__main__":
    main()
