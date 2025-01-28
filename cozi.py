#!/usr/bin/env python3

import os
import subprocess
import shutil
import sys
import time
import json
from pathlib import Path

COZI_DIR = os.path.expanduser("~/.config/Vencord/cozi")
PLUGIN_REPOS = os.path.join(COZI_DIR, "pluginRepos")
MAIN_REPO = os.path.join(COZI_DIR, "mainRepo")
PLUGIN_LIST = os.path.join(COZI_DIR, "pluginList.txt")
VERBOSE = False


def initialize_cozi():
    if not os.path.exists(COZI_DIR):
        color(34, "Initializing Cozi...")
        os.makedirs(PLUGIN_REPOS, exist_ok=True)
        open(PLUGIN_LIST, "a").close()

        color(32, "Cloning Vencord repository...")
        subprocess.run(
            [
                "git",
                "clone",
                "https://github.com/Vendicated/Vencord",
                MAIN_REPO,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        os.chdir(MAIN_REPO)
        subprocess.run(
            ["pnpm", "install", "--frozen-lockfile"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        color(32, "Cozi setup complete!")


def add_plugin(git_link):
    if not git_link:
        color(31, "Error: No git link or file provided.")
        exit(1)

    if os.path.isfile(git_link):
        color(32, f"Reading plugin links from file: {git_link}")
        with open(git_link, "r") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    add_single_plugin(line)

        color(32, "All plugins installed successfully!")
        color(33, "Now, enable with ./cozi patch")
    else:
        add_single_plugin(git_link)


def copy_plugin(repo_name):
    plugin_path = os.path.join(PLUGIN_REPOS, repo_name)
    dest_path = os.path.join(MAIN_REPO, "src", "userplugins", repo_name)

    if not os.path.isdir(plugin_path):
        color(31, f"Error: Plugin {repo_name} not found.")
        exit(1)

    color(32, f"Copying plugin: {repo_name}...")
    os.makedirs(os.path.join(MAIN_REPO, "src", "userplugins"), exist_ok=True)

    try:
        shutil.copytree(
            plugin_path,
            dest_path,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".git"),
        )
    except Exception as e:
        color(31, f"Failed to copy {repo_name}: {e}")
        exit(1)


def remove_plugin(repo_name):
    dest_path = os.path.join(MAIN_REPO, "src", "userplugins", repo_name)

    if not os.path.isdir(dest_path):
        color(31, f"Error: Plugin {repo_name} not found.")
        exit(1)

    color(32, f"Removing plugin: {repo_name}...")
    try:
        shutil.rmtree(dest_path)
    except Exception as e:
        color(31, f"Failed to remove {repo_name}: {e}")
        exit(1)


def delete_plugin(repo_name):
    if not repo_name:
        color(31, "Error: No repository name provided.")
        exit(1)

    plugin_path = os.path.join(PLUGIN_REPOS, repo_name)

    if not os.path.isdir(plugin_path):
        color(31, f"Error: Plugin {repo_name} not found.")
        exit(1)

    color(32, f"Deleting plugin repository: {repo_name}...")
    try:
        shutil.rmtree(plugin_path)
    except Exception as e:
        color(31, f"Failed to delete {repo_name}: {e}")
        exit(1)

    with open(PLUGIN_LIST, "r") as file:
        lines = file.readlines()

    with open(PLUGIN_LIST, "w") as file:
        for line in lines:
            if repo_name not in line:
                file.write(line)


def verbose_output(message):
    if VERBOSE:
        print(message)


def patch_vencord():
    print(color("32", "Building and injecting Vencord..."))
    try:
        os.chdir(MAIN_REPO)
    except FileNotFoundError:
        print(color("31", "Main repository directory not found."))
        sys.exit(1)

    try:
        subprocess.run(
            ["pnpm", "build"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        print(color("31", "Build failed."))
        sys.exit(1)

    print(color("32", "Attempting Auto-Patch"))

    # Disable user input for the auto-patch
    os.system("stty -echo -icanon")
    try:
        patch_process = subprocess.Popen(["pnpm", "inject"], stdin=subprocess.PIPE)
        time.sleep(2)
        patch_process.stdin.write(b"\033[B\r\x04")
        patch_process.stdin.flush()
        time.sleep(2)
        patch_process.stdin.write(b"[B\r\x04")
        patch_process.stdin.flush()

        patch_process.wait()

        inject_exit_code = patch_process.returncode
    finally:
        os.system("stty echo icanon")

    if inject_exit_code == 0:
        print(color("32", "Vencord successfully patched!"))
    else:
        print(color("31", "Vencord patching completed with errors."))


def update_plugins():
    print(color("32", "Updating all plugins..."))
    for plugin_dir in os.listdir(PLUGIN_REPOS):
        plugin_path = os.path.join(PLUGIN_REPOS, plugin_dir)
        if os.path.isdir(os.path.join(plugin_path, ".git")):
            print(color("33", f"Updating: {plugin_dir}"))
            try:
                subprocess.run(
                    ["git", "-C", plugin_path, "pull"],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                copy_plugin(plugin_dir)
            except subprocess.CalledProcessError:
                print(color("31", f"Failed to update {plugin_dir}."))
                sys.exit(1)
    print(color("32", "All plugins updated!"))


def uninstall_cozi():
    print(color("31", "Uninstalling Cozi and removing all related files..."))
    try:
        subprocess.run(["rm", "-rf", COZI_DIR], check=True)
    except subprocess.CalledProcessError:
        print(color("31", "Failed to remove Cozi directory."))
        sys.exit(1)
    print(color("32", "Cozi has been successfully uninstalled."))


def cozi_list():
    print(color("cyan", "\nInstalled Plugins:"))
    if os.path.isfile(PLUGIN_LIST) and os.path.getsize(PLUGIN_LIST) > 0:
        with open(PLUGIN_LIST, "r") as file:
            for line in file:
                git_link = line.strip()
                repo_name = os.path.basename(git_link).replace(".git", "")
                print(f"{color('33', 'Repo Name:')} {color('32', repo_name)}")
                print(f"{color('33', 'Git Link:')}  {color('34', git_link)}\n")
    else:
        print(color("31", "No plugins are installed."))


def cozi_help():
    print(
        color(
            "36",  # Cyan
            """
  ____ ___ ________ 
 / ___/ _ \\__  /_ _|
| |  | | | |/ / | | 
| |__| |_| / /_ | | 
 \\____\\___/____|___|
    """,
        )
    )
    print(color("35", "\n\nCozi - Vencord Plugin Manager"))
    print(color("34", "\nMade by 1337isnot1337"))
    print(color("35", "\nUsage: cozi [command] [arguments]"))
    print(color("35", "\nMain Commands:"))
    print(
        f"  {color('32', bold('add'))} [git link | file] - Add a plugin repository (single git link or file with git links)"
    )
    print(f"  {color('32', bold('patch'))}                 - Build & inject Vencord")
    print(color("35", "\nOther Commands:"))
    print(
        f"  {color('33', bold('delete'))} [repo name]    - Remove a specific plugin repository"
    )
    print(
        f"  {color('33', bold('export'))} [file]         - Export plugin configuration to a file"
    )
    print(
        f"  {color('33', bold('import'))} [file]         - Import plugin configuration from a file"
    )
    print(
        f"  {color('33', bold('list'))}                  - List all installed plugins"
    )
    print(
        f"  {color('33', bold('status'))}                - Display a detailed status report of Cozi"
    )
    print(f"  {color('33', bold('update'))}                - Update all plugins")
    print(
        f"  {color('33', bold('uninstall'))}             - Uninstall all cozi related files"
    )
    print(f"  {color('33', bold('help'))}                  - Show this help menu")
    print("")
    print(color("35", "Example:"))
    print(
        f"  {color('33', '    cozi')} {color('32', 'add')} {color('33', 'https://git.nin0.dev/userplugins/venfetch')} - Add Venfetch to plugins"
    )
    print(
        f"  {color('33', '    cozi')} {color('32', 'patch')} - Patch Vencord so you can use the plugin"
    )
    print("\nMake sure you enable the plugins in settings!")


def color(code, message):
    """Returns the ANSI-colored string instead of printing it."""
    return f"\033[{code}m{message}\033[0m"


def bold(message):
    """Helper function to make text bold."""
    return f"\033[1m{message}\033[0m"


def add_single_plugin(git_link):
    repo_name = Path(git_link).stem

    with open(PLUGIN_LIST, "r") as f:
        if git_link in f.read():
            color(33, f"Plugin {repo_name} already added.")
            return

    color(32, f"Adding plugin: {repo_name}...")

    try:
        subprocess.run(
            ["git", "clone", git_link, f"{PLUGIN_REPOS}/{repo_name}"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        color(31, f"Failed to clone {git_link}.")
        sys.exit(1)

    with open(PLUGIN_LIST, "a") as f:
        f.write(git_link + "\n")

    package_json = Path(MAIN_REPO) / "package.json"
    plugin_path = Path(PLUGIN_REPOS) / repo_name

    if not package_json.exists():
        color(31, "Error: package.json not found.")
        sys.exit(1)

    with open(package_json, "r") as f:
        package_data = json.load(f)
        installed_deps = set(package_data.get("dependencies", {}).keys()).union(
            package_data.get("devDependencies", {}).keys()
        )

    imports = set()
    for root, _, files in os.walk(plugin_path):
        for file in files:
            if file.endswith(".js") or file.endswith(".ts"):
                with open(Path(root) / file, "r") as f:
                    imports.update(
                        line.split("from")[-1].strip(" '" "\n")
                        for line in f
                        if "from" in line
                    )

    for imp in imports:
        if (
            not (imp.startswith(".") or imp.startswith("/"))
            and imp not in installed_deps
        ):
            color(33, f"Installing missing dependency: {imp}")
            try:
                subprocess.run(
                    ["pnpm", "install", imp, "--prefix", MAIN_REPO],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except subprocess.CalledProcessError:
                color(31, f"Failed to install {imp}.")
                sys.exit(1)

    copy_plugin(repo_name)


def cozi_export(file_path):
    if not file_path:
        color(31, "Error: No file path provided.")
        sys.exit(1)

    if not Path(file_path).parent.exists():
        color(31, "Error: Directory for file does not exist.")
        sys.exit(1)

    if not Path(PLUGIN_LIST).exists():
        color(31, "Error: Plugin list file not found. Are any plugins installed?")
        sys.exit(1)

    try:
        subprocess.run(
            ["cp", PLUGIN_LIST, file_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        color(32, f"Plugin configuration successfully exported to {file_path}.")
    except subprocess.CalledProcessError:
        color(31, "Failed to export plugin configuration.")
        sys.exit(1)


def cozi_import(import_file):
    if not import_file or not Path(import_file).exists():
        color(31, "Error: Invalid or missing file for import.")
        sys.exit(1)

    color(32, f"Importing plugin configuration from: {import_file}")

    with open(import_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                add_single_plugin(line)

    color(32, "All plugins imported successfully!")


def cozi_status():
    print(color(36, "\n=== Cozi Status Report ==="))

    if os.path.isdir(MAIN_REPO):
        print(color(33, f"Vencord Repository: {color(32, 'Found')}"))
        print(color(34, f"Path: {MAIN_REPO}"))
    else:
        print(
            color(31, "Error: Vencord repository not found. Did you initialize Cozi?")
        )
        return 1

    # Check for installed plugins
    try:
        with open(PLUGIN_LIST, "r") as f:
            plugins = f.read().splitlines()
    except FileNotFoundError:
        plugins = []

    if plugins:
        print(color(33, f"\nInstalled Plugins: {color(32, len(plugins))}"))
        for plugin in plugins:
            repo_name = os.path.basename(plugin).replace(".git", "")
            plugin_path = os.path.join(PLUGIN_REPOS, repo_name)

            if os.path.isdir(plugin_path):
                print(color(32, f"  - {repo_name}: {color(34, 'Installed')}"))
                print(color(34, f"    Repository: {plugin}"))
                try:
                    commit_hash = subprocess.check_output(
                        ["git", "-C", plugin_path, "rev-parse", "--short", "HEAD"],
                        text=True,
                    ).strip()
                    branch_name = subprocess.check_output(
                        ["git", "-C", plugin_path, "symbolic-ref", "--short", "HEAD"],
                        text=True,
                    ).strip()
                    print(
                        color(
                            34,
                            f"    Current Commit: {commit_hash} (Branch: {branch_name})",
                        )
                    )
                except subprocess.CalledProcessError:
                    print(color(31, "    Error: Unable to fetch commit details."))
            else:
                print(color(31, f"  - {repo_name}: {color(31, 'Missing')}"))
    else:
        print(color(31, "\nNo plugins installed."))

    # Check Node.js version
    try:
        node_version = subprocess.check_output(["node", "--version"], text=True).strip()
        print(color(33, f"\nNode.js Version: {color(32, node_version)}"))
    except FileNotFoundError:
        print(color(31, "\nError: Node.js is not installed or not in PATH."))

    # Check pnpm version
    try:
        pnpm_version = subprocess.check_output(["pnpm", "--version"], text=True).strip()
        print(color(33, f"pnpm Version: {color(32, pnpm_version)}"))
    except FileNotFoundError:
        print(color(31, "Error: pnpm is not installed or not in PATH."))

    # Check package.json dependencies
    package_json_path = os.path.join(MAIN_REPO, "package.json")
    if os.path.isfile(package_json_path):
        print(color(33, "\nDependencies in package.json:"))
        try:
            with open(package_json_path, "r") as f:
                package_data = json.load(f)
                dependencies = package_data.get("dependencies", {})
                if dependencies:
                    for dep in dependencies:
                        print(color(34, f"  - {dep}"))
                else:
                    print(color(31, "  No dependencies found."))
        except json.JSONDecodeError:
            print(color(31, "  Error: Unable to parse package.json."))
    else:
        print(color(31, f"\nError: package.json not found in {MAIN_REPO}."))

    # Check for untracked files in the Vencord repo
    try:
        untracked_files = subprocess.check_output(
            ["git", "-C", MAIN_REPO, "status", "--porcelain"], text=True
        ).strip()
        if untracked_files:
            print(color(33, "\nUntracked or Modified Files in Vencord Repository:"))
            for file in untracked_files.splitlines():
                print(color(34, f"  - {file}"))
        else:
            print(color(32, "\nNo untracked or modified files in Vencord repository."))
    except subprocess.CalledProcessError:
        print(color(31, "\nError: Unable to check Vencord repository status."))

    print(color(36, "\n=== End of Cozi Status Report ==="))


def main():
    initialize_cozi()
    if len(sys.argv) > 1 and sys.argv[1] in ("-v", "verbose"):
        global VERBOSE
        VERBOSE = True
        sys.argv.pop(1)

    if len(sys.argv) < 2:
        cozi_help()
        sys.exit(1)

    command = sys.argv[1]

    commands = {
        "add": add_plugin,
        "delete": delete_plugin,
        "export": cozi_export,
        "import": cozi_import,
        "list": cozi_list,
        "patch": patch_vencord,
        "status": cozi_status,
        "update": update_plugins,
        "uninstall": uninstall_cozi,
        "help": cozi_help,
    }

    if command in commands:
        if len(sys.argv) > 2:
            commands[command](sys.argv[2])
        else:
            commands[command]()
    else:
        cozi_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
