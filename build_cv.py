import subprocess
import sys
import os

def run_command(command):
    """
    Run a shell command and handle errors.
    """
    cmd_str = " ".join(command)
    print(f"[{cmd_str}] Running...")
    try:
        # Use subprocess.run to execute the command associated with the arguments
        subprocess.run(
            command,
            check=True, # Raises CalledProcessError on non-zero exit code
            text=True
        )
        print(f"[{cmd_str}] Success.\n")
    except subprocess.CalledProcessError as e:
        print(f"Error: Command '{cmd_str}' failed with exit code {e.returncode}.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Command '{command[0]}' not found. Is it installed?")
        sys.exit(1)

def main():
    # Ensure we are in the script's directory (assuming script is in parsed root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Step 1: Fetch latest publications
    print("--- Step 1: Updating Publications ---")
    run_command(["python3", "fetch_publications.py"])

    # Step 2: Compile LaTeX
    # We compile twice to ensure references/page numbers are correct if needed
    print("--- Step 2: Compiling CV with XeLaTeX ---")
    run_command(["xelatex", "-interaction=nonstopmode", "resume_cv.tex"])

    print("Build Pipeline Completed Successfully.")
    print("Output: resume_cv.pdf")

if __name__ == "__main__":
    main()
