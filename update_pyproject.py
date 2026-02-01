import os
import re
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Update pyproject.toml with specific torch dependencies.")
    parser.add_argument("target", nargs="?", default="./pyproject.toml", help="Path to pyproject.toml file")
    args = parser.parse_args()

    target_file = args.target
    if not os.path.exists(target_file):
        print(f"Error: Target file '{target_file}' does not exist.")
        sys.exit(1)

    print(f"Updating {target_file}...")

    with open(target_file, "r") as f:
        text = f.read()

    # If TORCH_VERSION is provided (e.g. 2.9.0), use it to determine bounds
    if os.getenv("TORCH_VERSION"):
        torch_ver = os.getenv("TORCH_VERSION")
        # Assuming semantic versioning: 2.9.0 -> >=2.9.0, <2.10.0
        parts = torch_ver.split('.')
        if len(parts) >= 2:
            major, minor = parts[0], parts[1]
            next_minor = int(minor) + 1
            new_spec = f'"torch>={major}.{minor}.0,<{major}.{next_minor}.0"'

            # Pattern to match any torch dependency with or without version specifiers
            # Matches: "torch", "torch>=2.8.0,<2.9.0", "torch>=2.9.0", etc.
            torch_pattern = r'"torch(?:[><=!~][^"]*)?(?:,\s*[^"]+)?"'

            matches = re.findall(torch_pattern, text)
            if matches:
                print(f"  Found torch specs: {matches}")
                print(f"  Replacing all with {new_spec}")
                text = re.sub(torch_pattern, new_spec, text)
            else:
                print(f"  No torch dependency found to replace")
        else:
            raise RuntimeError(f"Invalid TORCH_VERSION format: {torch_ver}. Expected semantic versioning (e.g., 2.9.0).")
    else:
        raise RuntimeError("TORCH_VERSION environment variable is required.")

    with open(target_file, "w") as f:
        f.write(text)

    print("Done.")

if __name__ == "__main__":
    main()
