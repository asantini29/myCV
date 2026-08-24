import argparse
import subprocess
import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CV_DIR = "cv"  # Directory where the CV LaTeX files are located
CV_SOURCE = "resume_cv.tex"  # Full CV
CV_SOURCE_SHORT = "resume_cv_short.tex"  # Same document minus the long-form sections

def latex_env():
    """
    Environment for LaTeX runs: awesome-cv.cls, fontawesome.sty and fonts/ are
    shared and live at the repo root, while each document is compiled from its
    own subfolder, so kpathsea needs the root on its search path.
    """
    env = os.environ.copy()
    env["TEXINPUTS"] = os.path.join(ROOT_DIR, "") + "//:" + env.get("TEXINPUTS", "")
    return env

def run_command(command, directory=None, env=None):
    """
    Run a shell command and handle errors.
    """
    if directory:
        print(f"Working directory: {directory}")
    
    cmd_str = " ".join(command)
    print(f"[{cmd_str}] Running...")
    try:
        # Use subprocess.run to execute the command associated with the arguments
        subprocess.run(
            command,
            check=True, # Raises CalledProcessError on non-zero exit code
            text=True,
            cwd=os.path.join(ROOT_DIR, directory) if directory else ROOT_DIR,
            env=env
        )
        print(f"[{cmd_str}] Success.\n")
    except subprocess.CalledProcessError as e:
        print(f"Error: Command '{cmd_str}' failed with exit code {e.returncode}.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Command '{command[0]}' not found. Is it installed?")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Fetch publications and compile the CV.")
    parser.add_argument(
        "--short",
        action="store_true",
        help="Build the short CV (drops contributed talks and the complete "
             "publication list), producing resume_cv_short.pdf"
    )
    args = parser.parse_args()
    source = CV_SOURCE_SHORT if args.short else CV_SOURCE

    # Ensure we are in the script's directory (assuming script is in parsed root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Step 1: Fetch latest publications
    print("--- Step 1: Updating Publications ---")
    run_command(["python3", "fetch_publications.py"])

    # Step 2: Compile LaTeX
    # We compile twice to ensure references/page numbers are correct if needed
    print(f"--- Step 2: Compiling {'short' if args.short else 'full'} CV with XeLaTeX ---")
     # Print current directory for debugging
    run_command(["xelatex", "-interaction=nonstopmode", source],
                directory=CV_DIR, env=latex_env())

    print("Build Pipeline Completed Successfully.")
    print(f"Output: {os.path.join(CV_DIR, source.replace('.tex', '.pdf'))}")

if __name__ == "__main__":
    main()
