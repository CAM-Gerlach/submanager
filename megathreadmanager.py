#!/usr/bin/env python3
"""
Generate, pin and update a regular megathread for a subreddit.
"""

# Standard library imports
import argparse
import datetime
import json
from pathlib import Path
import time

# Third party imports
import praw
import prawcore.exceptions


__version__ = "0.1.1"

# General constants
CONFIG_DIRECTORY = Path("~/.config/megathread_manager").expanduser()
CONFIG_PATH = CONFIG_DIRECTORY / "config.json"
CURRENT_DATETIME = datetime.datetime.now(datetime.timezone.utc)
USER_AGENT = f"praw:megathreadmanager:v{__version__} (by u/CAM-Gerlach)"

DEFAULT_CONFIG = {
    "new_thread_interval": "month",
    "pin_thread": "top",
    "post_title_template": ("{subreddit_name} Megathread "
                            "({current_datetime:%B %Y}, #{thread_number})"),
    "praw_credentials": {
        "client_id": "CLIENT_ID",
        "client_secret": "CLIENT_SECRET",
        },
    "praw_credentials_mod": {},
    "praw_credentials_post": {},
    "repeat_interval_s": 300,
    "subreddit_name": "YOURSUBNAME",
    "thread_number": 0,
    "thread_url": "",
    "wiki_page_name": "WIKIPAGENAME",
    "wiki_page_timestamp": 0,
    }


class ConfigError(RuntimeError):
    pass


class MegathreadSession:
    """Common cached state for managing megathreads."""

    def __init__(self, config):
        self.config = config
        self.reddit_mod = praw.Reddit(**{
            **config["praw_credentials"],
            **config["praw_credentials_mod"],
            **{"user_agent": USER_AGENT},
            })
        self.reddit_post = praw.Reddit(**{
            **config["praw_credentials"],
            **config["praw_credentials_post"],
            **{"user_agent": USER_AGENT},
            })
        self.subreddit_post = self.reddit_post.subreddit(
            config["subreddit_name"])
        self.subreddit_mod = self.reddit_mod.subreddit(
            config["subreddit_name"])
        self.wiki_page = self.subreddit_post.wiki[config["wiki_page_name"]]


def write_config(config, config_path=CONFIG_PATH):
    """Write the passed config to the default config path as JSON."""
    with open(config_path, mode="w",
              encoding="utf-8", newline="\n") as config_file:
        json.dump(config, config_file, indent=4)


def generate_config(config_path=CONFIG_PATH):
    """Generate a new, default configuration file for Megathread Manager."""
    Path(config_path).parent.mkdir(parents=True, exist_ok=True)
    write_config(DEFAULT_CONFIG, config_path=config_path)
    return DEFAULT_CONFIG


def load_config(return_default=False, config_path=CONFIG_PATH):
    """Load Megathread Manager's config file, creating it if nessesary."""
    if not Path(config_path).exists():
        generate_config(config_path=config_path)
    with open(config_path, mode="r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    if not config or (not return_default and config == DEFAULT_CONFIG):
        raise ConfigError(f"Config file at {config_path} needs to be set up.")
    return config


def generate_post_details(session):
    """Generate the title and post templates."""
    template_variables = {
        "current_datetime": CURRENT_DATETIME,
        "current_datetime_local": datetime.datetime.now(),
        "subreddit_name": session.config["subreddit_name"],
        "thread_number": session.config["thread_number"],
        }
    post_title = session.config["post_title_template"].format(
        **template_variables)
    post_text = session.wiki_page.content_md.format(**template_variables)
    return {"title": post_title, "selftext": post_text}


def update_current_thread(session):
    """Update the text of the current thread."""
    post_details = generate_post_details(session)
    current_thread = session.reddit_post.submission(
        url=session.config["thread_url"])
    current_thread.edit(post_details["selftext"])


def create_new_thread(session):
    """Create a new thread based on the title and post template."""
    session.config["thread_number"] += 1
    post_details = generate_post_details(session)

    new_thread = session.subreddit_post.submit(**post_details)
    new_thread.disable_inbox_replies()
    new_thread_mod = session.reddit_mod.submission(url=new_thread.url)
    new_thread_mod.mod.approve()

    if session.config["pin_thread"]:
        thread_url = session.config["thread_url"]
        bottom_sticky = session.config["pin_thread"] != "top"
        if thread_url:
            session.reddit_mod.submission(url=thread_url).mod.sticky(
                state=False)
        try:
            sticky_to_keep = session.subreddit_mod.sticky(number=1)
        except prawcore.exceptions.NotFound:
            sticky_to_keep = None
        new_thread_mod.mod.sticky(state=True, bottom=bottom_sticky)
        if sticky_to_keep:
            sticky_to_keep.mod.sticky(state=True)

    session.config["thread_url"] = new_thread.url


def manage_thread(session):
    """Manage the current thread, creating or updating it as nessesary."""
    wiki_updated = (session.wiki_page.revision_date
                    > session.config["wiki_page_timestamp"])
    interval = session.config["new_thread_interval"]
    last_post_timestamp = 0
    if session.config["thread_url"]:
        current_thread = session.reddit_mod.submission(
            url=session.config["thread_url"])
        last_post_timestamp = datetime.datetime.fromtimestamp(
            current_thread.created_utc, tz=datetime.timezone.utc)
    should_post_new_thread = not last_post_timestamp or (
        interval and (getattr(last_post_timestamp, interval)
                      != getattr(CURRENT_DATETIME, interval)))

    if wiki_updated or should_post_new_thread:
        if should_post_new_thread:
            create_new_thread(session)
        else:
            update_current_thread(session)
        session.config["wiki_page_timestamp"] = session.wiki_page.revision_date


def run_manage(config_path=CONFIG_PATH):
    """Load the config file and run the thread manager."""
    config = load_config(config_path=config_path)
    session = MegathreadSession(config=config)
    manage_thread(session)
    write_config(session.config, config_path=config_path)


def run_manage_loop(config_path=CONFIG_PATH, repeat=True):
    config = load_config(config_path=config_path)
    if repeat is True:
        repeat = config["repeat_interval_s"]
    while True:
        print(f"Running megathread manager for config at {config_path}")
        run_manage(config_path=config_path)
        print("Megathread manager run complete")
        if not repeat:
            break
        try:
            time_left_s = repeat
            while True:
                time_to_sleep_s = min((time_left_s, 1))
                time.sleep(time_to_sleep_s)
                time_left_s -= 1
                if time_left_s <= 0:
                    break
        except KeyboardInterrupt:
            print("Recieved keyboard interrupt; exiting")
            break


def main(sys_argv=None):
    """Main function for the Megathread Manager CLI and dispatch."""
    parser_main = argparse.ArgumentParser(
        description="Generate, post, update and pin a Reddit megathread.",
        argument_default=argparse.SUPPRESS)
    parser_main.add_argument(
        "--version",
        action="store_true",
        help="If passed, will print the version number and exit",
        )
    parser_main.add_argument(
        "-c, --config-file",
        help="The path to the config file to use, if not the default.",
        )
    parser_main.add_argument(
        "--repeat",
        nargs="?",
        default=False,
        const=True,
        type=int,
        metavar="N",
        help=("If passed, re-runs every N seconds, or the value from the "
              "config file variable repeat_interval_s if N isn't specified."),
        )
    parsed_args = parser_main.parse_args(sys_argv)

    if getattr(parsed_args, "version", False):
        print(f"Megathread Manager version {__version__}")
    else:
        try:
            run_manage_loop(**vars(parsed_args))
        except ConfigError as e:
            print(f"Default config file generated. {e}")


if __name__ == "__main__":
    main()
