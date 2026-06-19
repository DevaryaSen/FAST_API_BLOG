#!/usr/bin/env python3
"""Seed the blog with Game of Thrones characters and quotes.

Usage:
  uv run python seed_got.py              # skip if users already exist
  uv run python seed_got.py --clear      # wipe users/posts, then seed
  uv run python seed_got.py --force      # add missing users even if some exist
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, func, select

import models
from auth import hash_password
from database import AsyncSessionLocal, engine

# Shared demo password (min 8 chars). Change or delete these accounts in production.
SEED_PASSWORD = "Winter123!"

# username, email, [(title, content, likes, days_ago), ...]
GOT_DATA: list[tuple[str, str, list[tuple[str, str, int, int]]]] = [
    (
        "Ned Stark",
        "ned.stark@winterfell.gov",
        [
            (
                "The man who passes the sentence should swing the sword",
                "Honor is not a word in the North—it is how we live. "
                "A ruler who will not do the killing himself should not give the order.",
                42,
                30,
            ),
        ],
    ),
    (
        "Tyrion Lannister",
        "tyrion@casterlyrock.com",
        [
            (
                "I drink and I know things",
                "That's what I do: I drink and I know things. "
                "And when the world underestimates a Lannister dwarf, they usually regret it.",
                128,
                28,
            ),
            (
                "Never forget what you are",
                "Wear it like armor, and it can never be used to hurt you.",
                87,
                14,
            ),
        ],
    ),
    (
        "Daenerys Targaryen",
        "daenerys@dragonstone.net",
        [
            (
                "Dracarys",
                "Fire cannot kill a dragon. When you hear that word, you had best move.",
                256,
                25,
            ),
            (
                "I will take what is mine with fire and blood",
                "A queen is not afraid to remind the world who she is.",
                199,
                10,
            ),
        ],
    ),
    (
        "Jon Snow",
        "jon.snow@nightswatch.org",
        [
            (
                "My watch is ended",
                "I pledged myself to the Night's Watch. When the duty was done, "
                "I walked away—because some oaths matter more than the words on paper.",
                91,
                22,
            ),
        ],
    ),
    (
        "Cersei Lannister",
        "cersei@kingslanding.gov",
        [
            (
                "When you play the game of thrones, you win or you die",
                "There is no middle ground. Mercy is a luxury the crown cannot afford.",
                73,
                20,
            ),
        ],
    ),
    (
        "Tywin Lannister",
        "tywin@casterlyrock.com",
        [
            (
                "A lion does not concern himself with the opinions of a sheep",
                "Legacy is built by those who understand power—not by those who chase applause.",
                64,
                18,
            ),
        ],
    ),
    (
        "Arya Stark",
        "arya@winterfell.gov",
        [
            (
                "A girl has no name",
                "The Many-Faced God teaches that identity is a mask. "
                "I have worn many—and remembered every face on my list.",
                112,
                16,
            ),
        ],
    ),
    (
        "Ygritte",
        "ygritte@beyondthewall.org",
        [
            (
                "You know nothing, Jon Snow",
                "He was brave, and stupid, and mine—until the world tore us apart.",
                210,
                15,
            ),
        ],
    ),
    (
        "Lord Varys",
        "varys@kingslanding.gov",
        [
            (
                "Power resides where men believe it resides",
                "A clever spider listens more than he speaks. "
                "The realm is a wheel, and I intend to break it.",
                55,
                12,
            ),
        ],
    ),
    (
        "Petyr Baelish",
        "littlefinger@thevale.net",
        [
            (
                "Chaos is a ladder",
                "Chaos isn't a pit. Chaos is a ladder. Many who try to climb it fail "
                "and never get to try again.",
                88,
                11,
            ),
        ],
    ),
    (
        "Bronn",
        "bronn@sellsword.com",
        [
            (
                "I try to stay out of other people's battles",
                "Unless there's gold in it. Or wine. Preferably both.",
                76,
                9,
            ),
        ],
    ),
    (
        "The Hound",
        "sandor@clegane.com",
        [
            (
                "Fuck the king",
                "Kings and knights talk about honor. I've seen what honor buys you.",
                94,
                8,
            ),
        ],
    ),
    (
        "Oberyn Martell",
        "oberyn@dorne.gov",
        [
            (
                "Tell Cersei. I want her to know it was me.",
                "Vengeance is a dish best served with poetry—and a spear.",
                67,
                7,
            ),
        ],
    ),
    (
        "Samwell Tarly",
        "sam@citadel.edu",
        [
            (
                "I always wanted to be a wizard",
                "Turns out you don't need a wand—just books, courage, and friends "
                "who believe in you.",
                48,
                6,
            ),
        ],
    ),
    (
        "Hodor",
        "hodor@winterfell.gov",
        [
            (
                "Hodor",
                "Hodor hodor. Hodor hodor hodor. (Hold the door.)",
                300,
                5,
            ),
        ],
    ),
    (
        "Bran Stark",
        "bran@winterfell.gov",
        [
            (
                "Everything you did brought you where you are now",
                "The Three-Eyed Raven sees threads of time. "
                "What looked like fate was often choice.",
                39,
                4,
            ),
        ],
    ),
    (
        "Jaime Lannister",
        "jaime@kingsguard.gov",
        [
            (
                "The things I do for love",
                "They call me Kingslayer as if it were shame. "
                "I would do it again.",
                52,
                3,
            ),
        ],
    ),
    (
        "Melisandre",
        "melisandre@asshai.org",
        [
            (
                "The night is dark and full of terrors",
                "The Lord of Light shows visions in the flames. "
                "Not all of them are meant to comfort.",
                61,
                2,
            ),
        ],
    ),
]


async def clear_all(session) -> None:
    await session.execute(delete(models.Post))
    await session.execute(delete(models.PasswordResetToken))
    await session.execute(delete(models.User))
    await session.commit()
    print("Cleared all users and posts.")


async def seed(*, clear: bool, force: bool) -> None:
    async with AsyncSessionLocal() as session:
        if clear:
            await clear_all(session)

        count_result = await session.execute(select(func.count()).select_from(models.User))
        existing_users = count_result.scalar() or 0

        if existing_users and not force and not clear:
            print(
                f"Database already has {existing_users} user(s). "
                "Use --clear to reset or --force to add missing characters."
            )
            return

        created_users = 0
        created_posts = 0
        password_hash = hash_password(SEED_PASSWORD)

        for username, email, posts in GOT_DATA:
            result = await session.execute(
                select(models.User).where(
                    func.lower(models.User.username) == username.lower(),
                ),
            )
            user = result.scalars().first()

            if not user:
                user = models.User(
                    username=username,
                    email=email.lower(),
                    password_hash=password_hash,
                )
                session.add(user)
                await session.flush()
                created_users += 1
                print(f"  + user: {username}")
            elif force:
                print(f"  = user exists: {username}")

            for title, content, likes, days_ago in posts:
                result = await session.execute(
                    select(models.Post).where(
                        models.Post.user_id == user.id,
                        models.Post.title == title,
                    ),
                )
                if result.scalars().first():
                    continue

                post = models.Post(
                    title=title,
                    content=content,
                    user_id=user.id,
                    likes=likes,
                    date_posted=datetime.now(UTC) - timedelta(days=days_ago),
                )
                session.add(post)
                created_posts += 1

        await session.commit()
        print(f"\nDone. Created {created_users} users, {created_posts} posts.")
        print(f"Demo login password for all seed users: {SEED_PASSWORD}")
        print("Log in with any character email above (e.g. tyrion@casterlyrock.com).")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Game of Thrones blog data")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Delete all users and posts before seeding",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Add missing users/posts even if the database is not empty",
    )
    args = parser.parse_args()

    try:
        await seed(clear=args.clear, force=args.force)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())