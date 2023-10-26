import time
import os
import drive_helpers

logfile = os.path.join(drive_helpers.get_unturned_path(), "Logs", "Client.log")
print(f"Extracting logs from: {logfile}")
# Keep track of the last line number that was read
last_line = 0

# if a log line has any of these strings in it, ignore it
IGNORE_SENTENCES = ["Look rotation viewing vector is zero"]

while True:
    # Get the size of the log file
    size = os.path.getsize(logfile)

    # If the size of the file has decreased (e.g., due to log rotation),
    # reset the last_line variable to the beginning of the file
    if size < last_line:
        last_line = 0

    # Open the file and seek to the last line that was read
    with open(logfile, encoding="utf-8") as f:
        f.seek(last_line)

        # Read any new lines and print them
        for line in f:
            # Avoid dumping entire log contents on startup
            if last_line > 0:
                if not any(s in line for s in IGNORE_SENTENCES):
                    print(line.strip())

        # Update the last_line variable to the current position
        if last_line == 0:
            print("Logs extracted, monitoring for updates...")
        last_line = f.tell()

    # Wait for a few seconds before checking again
    time.sleep(0.1)
