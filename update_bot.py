import discord
from discord.ext import commands
from github import Github
import zipfile
import os
import subprocess
import platform
from datetime import datetime, timezone
import time
import asyncio
import json

# Load configuration from JSON
def load_config():
    """Load configuration from config.json file"""
    config_path = 'config.json'
    if not os.path.exists(config_path):
        print(f"ERROR: {config_path} not found!")
        print("Please copy config.json.example to config.json and fill in your values.")
        exit(1)

    with open(config_path, 'r') as f:
        return json.load(f)

_config = load_config()

# Detect operating system
IS_WINDOWS = platform.system() == 'Windows'
IS_UNIX = platform.system() in ('Linux', 'Darwin')  # Linux or macOS

# ============= CONFIGURATION =============
class Config:
    # Discord & GitHub
    DISCORD_TOKEN = _config['discord']['bot_token']
    GITHUB_TOKEN = _config['github']['token']
    GITHUB_REPO = _config['github']['repo']
    BRANCH = _config['github'].get('branch', 'main')

    # Local paths
    # If USE_RWD is truthy, the bot will run against the current working directory
    # (or the path in LOCAL_REPO_PATH) instead of cloning
    USE_RWD = _config['repository'].get('use_rwd', False)

    if USE_RWD:
        LOCAL_REPO_PATH = _config['repository'].get('local_repo_path') or os.getcwd()
        MOD_SOURCE_FOLDER = LOCAL_REPO_PATH
    else:
        LOCAL_REPO_PATH = _config['repository'].get('local_repo_path', './repo_clone')
        MOD_SOURCE_FOLDER = _config['repository'].get('mod_source_folder') or LOCAL_REPO_PATH

    # Static file names
    PK3_NAME = _config['build']['pk3_name']
    RELEASE_ZIP_NAME = "release.zip"

    # Optional: restrict deploy command to role IDs (list)
    DEPLOY_ROLE_ID = _config['deploy'].get('role_ids', [])

    # Optional commands to run locally to stop/start the game server process
    SERVER_STOP_CMD = _config['server'].get('stop_cmd', '')
    SERVER_START_CMD = _config['server'].get('start_cmd', '')
    START_CMD_DIR = _config['server'].get('start_cmd_dir', '')

    # Server verification commands
    SERVER_STOP_VERIFY_CMD = _config['server'].get('stop_verify_cmd', '')
    SERVER_START_VERIFY_CMD = _config['server'].get('start_verify_cmd', '')

    # Start delay (for verification timeout)
    SERVER_START_DELAY = int(_config['server'].get('start_delay', 0))

    # Local MBII installation path (optional)
    # If set, the PK3 will be copied to this directory after stopping the server
    MBII_DIR = _config['mbii'].get('dir', '')

# ============= BOT SETUP =============

def _member_has_deploy_role(member):
    """Return (True, None) if member may deploy, otherwise (False, reason)."""
    # Allow administrators
    if member.guild_permissions.administrator:
        print(f"✓ {member.name} authorized as administrator")
        return True, None

    role_cfg = Config.DEPLOY_ROLE_ID
    if not role_cfg:
        print(f"✗ {member.name} denied: No deploy role IDs configured")
        return False, "Deployment restricted to server administrators (no deploy role IDs configured)."

    # Convert string IDs to integers
    try:
        allowed_ids = {int(role_id) for role_id in role_cfg if role_id}
    except (ValueError, TypeError):
        print(f"✗ Invalid deploy role IDs: {role_cfg}")
        return False, "Invalid deploy role IDs configured (must be integers)."

    print(f"Checking {member.name}'s roles against allowed IDs: {allowed_ids}")
    print(f"User has roles: {[f'{r.name} (ID: {r.id})' for r in member.roles]}")

    for role in member.roles:
        if role.id in allowed_ids:
            print(f"✓ {member.name} authorized via role: {role.name} (ID: {role.id})")
            return True, None

    print(f"✗ {member.name} denied: No matching role found")
    return False, f"You don't have the required role to run this command. Required role ID(s): {', '.join(map(str, allowed_ids))}"

def _check_deploy_role(ctx):
    """Command check wrapper for _member_has_deploy_role"""
    if ctx.guild is None:
        raise commands.CheckFailure("This command must be used in a server/guild.")

    allowed, reason = _member_has_deploy_role(ctx.author)
    if not allowed:
        raise commands.CheckFailure(reason)
    return True
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')
    print(f'Repository: {Config.GITHUB_REPO} (branch: {Config.BRANCH})')
    print(f'PK3: {Config.PK3_NAME}')
    print(f'Release: {Config.RELEASE_ZIP_NAME}')
    await bot.change_presence(activity=discord.Game(name="!deploy <version>"))
    print("Bot ready! Use !deploy, !status, or !help_deploy commands.")

# ============= HELPER FUNCTIONS =============

def ensure_repo_on_main():
    """Clone or pull latest from main branch"""
    repo_url = f"https://github.com/{Config.GITHUB_REPO}.git"
    # If configured to run from the current RWD, operate on that path instead of cloning
    if Config.USE_RWD:
        path = Config.LOCAL_REPO_PATH
        if not os.path.exists(path):
            raise Exception(f"Configured to run from RWD at {path}, but path does not exist.")
        if not os.path.exists(os.path.join(path, '.git')):
            raise Exception(f"Configured to run from RWD at {path}, but .git directory not found. Ensure this is a git repo or disable RWD mode.")

        print(f"Using existing repo at {path}, force updating from {Config.BRANCH}...")
        original_dir = os.getcwd()
        os.chdir(path)

        # Checkout the branch
        subprocess.run(['git', 'checkout', Config.BRANCH], capture_output=True)

        # Fetch latest changes
        subprocess.run(['git', 'fetch', 'origin', Config.BRANCH], capture_output=True)

        # Hard reset to remote branch (discards all local changes)
        result = subprocess.run(
            ['git', 'reset', '--hard', f'origin/{Config.BRANCH}'],
            capture_output=True,
            text=True
        )
        os.chdir(original_dir)

        if result.returncode != 0:
            raise Exception(f"Git reset failed: {result.stderr}")
    else:
        if not os.path.exists(Config.LOCAL_REPO_PATH):
            print(f"Cloning {repo_url}...")
            result = subprocess.run(
                ['git', 'clone', '-b', Config.BRANCH, repo_url, Config.LOCAL_REPO_PATH],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise Exception(f"Git clone failed: {result.stderr}")
        else:
            print(f"Force updating from {Config.BRANCH} into {Config.LOCAL_REPO_PATH}...")
            original_dir = os.getcwd()
            os.chdir(Config.LOCAL_REPO_PATH)

            # Checkout the branch
            subprocess.run(['git', 'checkout', Config.BRANCH], capture_output=True)

            # Fetch latest changes
            subprocess.run(['git', 'fetch', 'origin', Config.BRANCH], capture_output=True)

            # Hard reset to remote branch (discards all local changes)
            result = subprocess.run(
                ['git', 'reset', '--hard', f'origin/{Config.BRANCH}'],
                capture_output=True,
                text=True
            )

            os.chdir(original_dir)

            if result.returncode != 0:
                raise Exception(f"Git reset failed: {result.stderr}")
    
    print(f"✓ Repository updated from {Config.BRANCH}")

def create_pk3(source_folder):
    pk3_path = Config.PK3_NAME

    if os.path.exists(pk3_path):
        os.remove(pk3_path)

    print(f"Creating {pk3_path}...")

    file_count = 0
    with zipfile.ZipFile(pk3_path, 'w', zipfile.ZIP_DEFLATED) as pk3:
        for root, dirs, files in os.walk(source_folder):
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'python', 'node_modules', '.github']]

            for file in files:
                file_path = os.path.join(root, file)

                # Skip the PK3 file itself to prevent recursion
                if os.path.abspath(file_path) == os.path.abspath(pk3_path):
                    continue

                # Skip unwanted files by extension
                if file.startswith('.') or file.endswith((
                    '.py', '.pyc', '.log', '.tmp', '.bak',  # Original exclusions
                    '.sh', '.example', '.vbs', '.json', '.env', '.bat', '.txt', '.cmd', '.md', '.pk3'  # New exclusions
                )):
                    continue

                arcname = os.path.relpath(file_path, source_folder)

                pk3.write(file_path, arcname)
                file_count += 1

    size_mb = os.path.getsize(pk3_path) / (1024 * 1024)
    print(f"✓ Created {pk3_path} ({file_count} files, {size_mb:.2f} MB)")

    return pk3_path

def create_release_zip(pk3_file):
    """Create release.zip containing the pk3"""
    release_path = Config.RELEASE_ZIP_NAME
    
    if os.path.exists(release_path):
        os.remove(release_path)
    
    print(f"Creating {release_path}...")
    
    with zipfile.ZipFile(release_path, 'w', zipfile.ZIP_DEFLATED) as release_zip:
        # Add the pk3
        release_zip.write(pk3_file, Config.PK3_NAME)
        
        # Optionally add README.md (as README.txt) if present in the repo
        readme_path = os.path.join(Config.LOCAL_REPO_PATH, 'README.md')
        if os.path.exists(readme_path):
            release_zip.write(readme_path, 'README.txt')

    size_mb = os.path.getsize(release_path) / (1024 * 1024)
    print(f"✓ Created {release_path} ({size_mb:.2f} MB)")

    return release_path


def check_tag_version(tag):
    """Check if tag already exists or is older than latest release.

    Returns: (is_valid, error_message, latest_tag)
    """
    try:
        g = Github(Config.GITHUB_TOKEN)
        repo = g.get_repo(Config.GITHUB_REPO)

        # Get all releases
        releases = list(repo.get_releases())

        if not releases:
            # No existing releases, any tag is valid
            return True, None, None

        latest_tag = releases[0].tag_name

        # Check if tag already exists
        existing_tags = [r.tag_name for r in releases]
        if tag in existing_tags:
            return False, f"Tag `{tag}` already exists. Use a new version number.", latest_tag

        # Parse version numbers for comparison (assuming format like v1.2.3)
        def parse_version(ver_tag):
            """Parse version tag like 'v1.2.3' into tuple (1, 2, 3)"""
            try:
                # Remove 'v' prefix and split by '.'
                ver_str = ver_tag.lstrip('v')
                return tuple(int(x) for x in ver_str.split('.'))
            except (ValueError, AttributeError):
                # If parsing fails, return None to skip comparison
                return None

        new_ver = parse_version(tag)
        latest_ver = parse_version(latest_tag)

        # Only compare if both versions parsed successfully
        if new_ver and latest_ver:
            if new_ver <= latest_ver:
                return False, f"Tag `{tag}` is not newer than the latest release `{latest_tag}`. Use a higher version number.", latest_tag

        # Tag is valid
        return True, None, latest_tag

    except Exception as e:
        print(f"Warning: Could not check tag version: {e}")
        # If we can't check, allow the deployment (fail open)
        return True, None, None


def create_github_release(tag, release_zip):
    """Create GitHub release with specified tag"""
    g = Github(Config.GITHUB_TOKEN)
    repo = g.get_repo(Config.GITHUB_REPO)

    # Generate changelog from commits since last release
    try:
        releases = list(repo.get_releases())
        if releases:
            last_tag = releases[0].tag_name
            comparison = repo.compare(last_tag, Config.BRANCH)
            commits = list(comparison.commits)
        else:
            commits = list(repo.get_commits(sha=Config.BRANCH)[:10])

        if commits:
            changelog = "## Changes\n\n"
            for commit in commits:
                msg = commit.commit.message.split('\n')[0]
                author = commit.author.login if commit.author else "Unknown"
                changelog += f"- {msg} (@{author})\n"
        else:
            changelog = "No new changes since last release."
    except Exception as e:
        print(f"Warning: Could not generate changelog: {e}")
        changelog = "Release created via Discord bot."

    print(f"Creating GitHub release {tag}...")

    release = repo.create_git_release(
        tag=tag,
        name=tag,
        message=changelog,
        draft=False,
        prerelease=False,
        target_commitish=Config.BRANCH
    )

    print(f"Uploading {Config.RELEASE_ZIP_NAME}...")
    release.upload_asset(
        release_zip,
        content_type="application/zip"
    )

    print(f"✓ Release published: {release.html_url}")
    return release


def _run_local_command(cmd, timeout=30, cwd=None):
    """Run a command locally.

    Args:
        cmd: The command to run
        timeout: Timeout in seconds (default 30)
        cwd: Working directory (default None = current directory)

    Returns: (exit_code, stdout, stderr)
    """
    if not cmd:
        return 0, "", ""

    try:
        # Use provided working directory if specified
        if cwd:
            print(f"Running command in directory: {cwd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        # Command timed out - assume it succeeded and moved to background
        print(f"Command timed out after {timeout}s, assuming success and continuing...")
        return 0, "", f"Command timed out after {timeout}s"

def copy_to_mbii_dir(pk3_file):
    """Copy the PK3 file to local MBII installation directory"""
    if not Config.MBII_DIR:
        return False

    import shutil

    if not os.path.exists(Config.MBII_DIR):
        raise Exception(f"MBII directory does not exist: {Config.MBII_DIR}")

    dest_path = os.path.join(Config.MBII_DIR, Config.PK3_NAME)
    file_size = os.path.getsize(pk3_file)

    print(f"Copying {Config.PK3_NAME} to {Config.MBII_DIR}...")
    shutil.copy2(pk3_file, dest_path)

    # Verify copy
    if os.path.exists(dest_path) and os.path.getsize(dest_path) == file_size:
        print(f"✓ Copied to: {dest_path}")
        return True
    else:
        raise Exception(f"Failed to copy PK3 to MBII directory")

# ============= DISCORD COMMANDS =============

@bot.command()
@commands.check(_check_deploy_role)
async def deploy(ctx, tag: str):
    # Validate tag format (optional but recommended)
    if not tag.startswith('v'):
        await ctx.send(f"⚠️ Tag should start with 'v' (e.g., v1.0.0). Proceeding with `{tag}`...")

    # Check if tag already exists or is older than latest
    is_valid, error_msg, latest_tag = check_tag_version(tag)
    if not is_valid:
        embed = discord.Embed(
            title="❌ Deployment Rejected",
            description=error_msg,
            color=discord.Color.red(),
            timestamp=datetime.now(timezone.utc)
        )
        if latest_tag:
            embed.add_field(name="Latest Release", value=f"`{latest_tag}`", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)
        return

    # Create status embed
    embed = discord.Embed(
        title="🚀 Deploying Assets",
        description=f"Version: `{tag}` | Branch: `{Config.BRANCH}`",
        color=discord.Color.blue(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.set_footer(text=f"Requested by {ctx.author.display_name}")

    status_msg = await ctx.send(embed=embed)

    try:
        # Determine total steps based on what's enabled
        total_steps = 4  # Always: pull, pk3, release.zip, github
        if Config.SERVER_STOP_CMD or Config.MBII_DIR or Config.SERVER_START_CMD:
            total_steps += 1  # Server operations (stop/transfer/start combined)

        current_step = 0

        # Step 1: Pull from main
        current_step += 1
        embed.add_field(name=f"📥 Step {current_step}/{total_steps}", value="Pulling from main branch...", inline=False)
        await status_msg.edit(embed=embed)
        ensure_repo_on_main()
        embed.set_field_at(-1, name=f"✅ Step {current_step}/{total_steps}", value="Pull complete", inline=False)
        await status_msg.edit(embed=embed)

        # Step 2: Create pk3
        current_step += 1
        embed.add_field(name=f"📦 Step {current_step}/{total_steps}", value=f"Creating {Config.PK3_NAME}...", inline=False)
        await status_msg.edit(embed=embed)
        pk3_file = create_pk3(Config.MOD_SOURCE_FOLDER)
        embed.set_field_at(-1, name=f"✅ Step {current_step}/{total_steps}", value=f"Created {Config.PK3_NAME} ({os.path.getsize(pk3_file) / (1024*1024):.2f} MB)", inline=False)
        await status_msg.edit(embed=embed)

        # Step 3: Create release.zip
        current_step += 1
        embed.add_field(name=f"🗜️ Step {current_step}/{total_steps}", value=f"Creating {Config.RELEASE_ZIP_NAME}...", inline=False)
        await status_msg.edit(embed=embed)
        release_zip = create_release_zip(pk3_file)
        embed.set_field_at(-1, name=f"✅ Step {current_step}/{total_steps}", value=f"Created {Config.RELEASE_ZIP_NAME} ({os.path.getsize(release_zip) / (1024*1024):.2f} MB)", inline=False)
        await status_msg.edit(embed=embed)

        # Step 4: GitHub release
        current_step += 1
        embed.add_field(name=f"📤 Step {current_step}/{total_steps}", value=f"Publishing release {tag}...", inline=False)
        await status_msg.edit(embed=embed)
        release = create_github_release(tag, release_zip)
        embed.set_field_at(-1, name=f"✅ Step {current_step}/{total_steps}", value=f"Release published: [Link]({release.html_url})", inline=False)
        await status_msg.edit(embed=embed)

        # Combined server operations step (stop/transfer/start)
        if Config.SERVER_STOP_CMD or Config.MBII_DIR or Config.SERVER_START_CMD:
            current_step += 1

            # Stop server process (if configured)
            if Config.SERVER_STOP_CMD:
                embed.add_field(name=f"⏹️ Step {current_step}/{total_steps}", value="Stopping server process...", inline=False)
                await status_msg.edit(embed=embed)
                code, out, err = _run_local_command(Config.SERVER_STOP_CMD, timeout=5)
                if code != 0:
                    # Don't fail deployment if stop fails (server might already be stopped)
                    print(f"Warning: Stop command returned exit code {code}")
                    print(f"STDOUT: {out}")
                    print(f"STDERR: {err}")
                    embed.set_field_at(-1, name=f"⚠️ Step {current_step}/{total_steps}", value="Stop command completed with warnings (server may already be stopped)", inline=False)
                else:
                    embed.set_field_at(-1, name=f"✅ Step {current_step}/{total_steps}", value="Stop command completed", inline=False)
                await status_msg.edit(embed=embed)

                # Verify stop if a verify command is provided
                if Config.SERVER_STOP_VERIFY_CMD:
                    embed.set_field_at(-1, name=f"🔍 Step {current_step}/{total_steps}", value="Verifying server stopped...", inline=False)
                    await status_msg.edit(embed=embed)

                    start = time.time()
                    verified = False
                    timeout = max(1, Config.SERVER_START_DELAY)
                    while time.time() - start < timeout:
                        v_code, v_out, v_err = _run_local_command(Config.SERVER_STOP_VERIFY_CMD)
                        if v_code == 0:
                            verified = True
                            break
                        time.sleep(1)

                    if not verified:
                        raise Exception(f"Server stop verification failed after {timeout} seconds. Last exit {v_code}\nSTDOUT:\n{v_out}\nSTDERR:\n{v_err}")
                    embed.set_field_at(-1, name=f"✅ Step {current_step}/{total_steps}", value="Server stopped and verified", inline=False)
                    await status_msg.edit(embed=embed)

                elif Config.SERVER_START_DELAY and Config.SERVER_START_DELAY > 0:
                    # No verify cmd: use start delay as wait time
                    embed.set_field_at(-1, name=f"⏳ Step {current_step}/{total_steps}", value=f"Waiting {Config.SERVER_START_DELAY}s...", inline=False)
                    await status_msg.edit(embed=embed)
                    time.sleep(Config.SERVER_START_DELAY)
                    embed.set_field_at(-1, name=f"✅ Step {current_step}/{total_steps}", value="Wait complete", inline=False)
                    await status_msg.edit(embed=embed)

            # Copy PK3 to local MBII directory (if configured)
            if Config.MBII_DIR:
                embed.set_field_at(-1, name=f"📁 Step {current_step}/{total_steps}", value="Transferring PK3...", inline=False)
                await status_msg.edit(embed=embed)
                copy_to_mbii_dir(pk3_file)
                embed.set_field_at(-1, name=f"✅ Step {current_step}/{total_steps}", value="PK3 transferred", inline=False)
                await status_msg.edit(embed=embed)

            # Start server (if configured)
            if Config.SERVER_START_CMD:
                embed.set_field_at(-1, name=f"▶️ Step {current_step}/{total_steps}", value="Starting server...", inline=False)
                await status_msg.edit(embed=embed)

                cwd = Config.START_CMD_DIR if Config.START_CMD_DIR else None
                if cwd:
                    # Normalize path to handle forward slashes on Windows
                    cwd = os.path.normpath(cwd)
                    print(f"Running start command in directory: {cwd}")

                try:
                    if IS_WINDOWS:
                        # Windows: Use 'start' command to open in new console window
                        # This ensures the batch file and any Python scripts it runs get their own window
                        if cwd:
                            # If we have a working directory, use /D flag with quoted path
                            # DO NOT pass cwd to Popen when using start /D - it causes conflicts with spaces
                            cmd = f'start /D "{cwd}" "" {Config.SERVER_START_CMD}'
                            popen_cwd = None  # Let start /D handle the directory
                        else:
                            # Otherwise just use start with empty title
                            cmd = f'start "" {Config.SERVER_START_CMD}'
                            popen_cwd = None

                        # Create minimal clean environment with only essential system variables
                        # This prevents bot's DISCORD_BOT_TOKEN from leaking but keeps system functional
                        clean_env = {
                            'SYSTEMROOT': os.environ.get('SYSTEMROOT', 'C:\\Windows'),
                            'SYSTEMDRIVE': os.environ.get('SYSTEMDRIVE', 'C:'),
                            'PATH': os.environ.get('PATH', ''),
                            'PATHEXT': os.environ.get('PATHEXT', '.COM;.EXE;.BAT;.CMD'),
                            'COMSPEC': os.environ.get('COMSPEC', 'C:\\Windows\\system32\\cmd.exe'),
                            'TEMP': os.environ.get('TEMP', ''),
                            'TMP': os.environ.get('TMP', ''),
                        }

                        subprocess.Popen(
                            cmd,
                            shell=True,
                            cwd=popen_cwd,
                            env=clean_env  # Clean environment without bot credentials
                        )
                        print(f"✓ Started server process in new console window with clean environment")

                    elif IS_UNIX:
                        # Unix/Linux: Use nohup to run in background and detach from terminal
                        # Make the script executable if it isn't already
                        script_path = os.path.join(cwd, Config.SERVER_START_CMD) if cwd else Config.SERVER_START_CMD
                        if os.path.exists(script_path):
                            os.chmod(script_path, 0o755)

                        # Create minimal clean environment
                        clean_env = {
                            'PATH': os.environ.get('PATH', '/usr/local/bin:/usr/bin:/bin'),
                            'HOME': os.environ.get('HOME', ''),
                            'USER': os.environ.get('USER', ''),
                            'SHELL': os.environ.get('SHELL', '/bin/bash'),
                            'TMPDIR': os.environ.get('TMPDIR', '/tmp'),
                        }

                        # Use nohup to run in background, redirect output to log file
                        cmd = f'nohup {Config.SERVER_START_CMD} > server_start.log 2>&1 &'

                        subprocess.Popen(
                            cmd,
                            shell=True,
                            cwd=cwd if cwd else None,
                            env=clean_env,
                            start_new_session=True  # Detach from current process group
                        )
                        print(f"✓ Started server process in background with clean environment")

                    else:
                        print(f"Warning: Unsupported OS: {platform.system()}")
                        raise Exception(f"Unsupported operating system: {platform.system()}")

                except Exception as e:
                    print(f"Warning: Error starting server: {e}")

                # Verify start if a verify command is provided
                if Config.SERVER_START_VERIFY_CMD:
                    embed.set_field_at(-1, name=f"🔍 Step {current_step}/{total_steps}", value="Verifying server started...", inline=False)
                    await status_msg.edit(embed=embed)

                    start = time.time()
                    verified = False
                    timeout = max(15, Config.SERVER_START_DELAY)  # At least 15 seconds to verify
                    while time.time() - start < timeout:
                        v_code, v_out, v_err = _run_local_command(Config.SERVER_START_VERIFY_CMD, timeout=5)
                        if v_code == 0:
                            verified = True
                            break
                        await asyncio.sleep(1)

                    if verified:
                        embed.set_field_at(-1, name=f"✅ Step {current_step}/{total_steps}", value="Server started and verified running", inline=False)
                    else:
                        embed.set_field_at(-1, name=f"⚠️ Step {current_step}/{total_steps}", value=f"Server start command executed (verification timed out after {timeout}s)", inline=False)
                else:
                    embed.set_field_at(-1, name=f"✅ Step {current_step}/{total_steps}", value="Server start command executed", inline=False)

                await status_msg.edit(embed=embed)

        # Cleanup temporary files
        print(f"Cleaning up temporary files: {pk3_file}, {release_zip}")
        if os.path.exists(pk3_file):
            os.remove(pk3_file)
            print(f"✓ Deleted {pk3_file}")
        if os.path.exists(release_zip):
            os.remove(release_zip)
            print(f"✓ Deleted {release_zip}")

        # Success! Clear all previous steps and show final message
        embed.clear_fields()
        embed.color = discord.Color.gold()  # Yellow color
        embed.title = "Build is a success!"
        embed.description = f"Version `{tag}` deployed successfully"

        embed.add_field(
            name="🔗 GitHub Release",
            value=f"[{tag}]({release.html_url})",
            inline=False
        )

        await status_msg.edit(embed=embed)
        
    except Exception as e:
        embed.color = discord.Color.red()
        embed.title = "❌ Deployment Failed"
        embed.add_field(name="Error", value=f"```{str(e)}```", inline=False)
        await status_msg.edit(embed=embed)
        print(f"Deployment error: {e}")
        import traceback
        traceback.print_exc()


# Slash commands removed - using chat commands only (!deploy, !status, !help_deploy)

@bot.command()
async def status(ctx):
    """Check latest release info"""
    try:
        g = Github(Config.GITHUB_TOKEN)
        repo = g.get_repo(Config.GITHUB_REPO)
        
        releases = list(repo.get_releases())
        
        embed = discord.Embed(
            title="📊 Release Status",
            color=discord.Color.blue()
        )
        
        if releases:
            latest = releases[0]
            
            # Get asset info
            assets = list(latest.get_assets())
            downloads = sum(a.download_count for a in assets)
            
            embed.add_field(name="Latest Version", value=f"`{latest.tag_name}`", inline=True)
            embed.add_field(name="Released", value=latest.created_at.strftime("%Y-%m-%d %H:%M"), inline=True)
            embed.add_field(name="Downloads", value=str(downloads), inline=True)
            
            # Show files in release
            file_list = "\n".join([f"• `{a.name}` ({a.size / (1024*1024):.2f} MB)" for a in assets])
            embed.add_field(name="Files", value=file_list or "No files", inline=False)
            
            embed.add_field(name="Link", value=f"[View Release]({latest.html_url})", inline=False)
        else:
            embed.description = "No releases yet!\nUse `!deploy <version>` to create the first release."
        
        embed.add_field(name="Repository", value=f"`{Config.GITHUB_REPO}`", inline=True)
        embed.add_field(name="Branch", value=f"`{Config.BRANCH}`", inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error fetching status: {str(e)}")

@bot.command()
async def help_deploy(ctx):
    """Show deployment help"""
    embed = discord.Embed(
        title="🤖 Release Deployment Bot",
        description="Automated deployment from GitHub to your game server",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="!deploy <version>",
        value="Deploy a new version (e.g., `!deploy v1.2.3`)\nPulls from main branch, packages, and uploads",
        inline=False
    )
    
    embed.add_field(
        name="!status",
        value="Show current release information",
        inline=False
    )
    
    embed.add_field(
        name="Files Created",
        value=f"• `{Config.PK3_NAME}` (uploaded to server)\n• `{Config.RELEASE_ZIP_NAME}` (on GitHub)",
        inline=False
    )
    
    embed.add_field(
        name="Configuration",
        value=f"Repository: `{Config.GITHUB_REPO}`\nBranch: `{Config.BRANCH}`",
        inline=False
    )

    embed.add_field(
        name="Run Mode",
        value=f"{'RWD (using existing path)' if Config.USE_RWD else 'Clone mode (using LOCAL_REPO_PATH)'} → `{Config.LOCAL_REPO_PATH}`",
        inline=False
    )
    
    await ctx.send(embed=embed)

@deploy.error
async def deploy_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need administrator permissions to deploy!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `!deploy <version>` (e.g., `!deploy v1.0.0`)")
    elif isinstance(error, commands.CheckFailure):
        # Provide a friendly message for role/permission check failures
        await ctx.send(f"❌ Permission denied: {str(error)}")
    else:
        await ctx.send(f"❌ Error: {str(error)}")

# ============= START BOT =============
if __name__ == "__main__":
    # Validate config
    if not Config.DISCORD_TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN not found in .env!")
        exit(1)
    
    if not Config.GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN not found in .env!")
        exit(1)
    
    print("=" * 60)
    print("Release Deployment Bot")
    print("=" * 60)
    print(f"Repository: {Config.GITHUB_REPO}")
    print(f"Branch:     {Config.BRANCH}")
    print(f"PK3:        {Config.PK3_NAME}")
    print(f"Release:    {Config.RELEASE_ZIP_NAME}")
    print(f"Run mode:   {'RWD (using existing path)' if Config.USE_RWD else 'Clone mode (uses LOCAL_REPO_PATH)'} -> {Config.LOCAL_REPO_PATH}")
    print("=" * 60)
    
    bot.run(Config.DISCORD_TOKEN)