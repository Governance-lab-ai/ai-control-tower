import argparse

from app.core.config import get_settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.services.seed import clear_all_application_data, clear_demo_data, seed_demo_systems


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Governance Control Tower management commands.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init-db", help="Apply migrations and run configured startup seed behaviour.")
    subparsers.add_parser("seed-demo", help="Seed synthetic local showcase systems, runs, and evaluations.")
    subparsers.add_parser("seed-showcase", help="Alias for seed-demo with product showcase wording.")
    subparsers.add_parser("clear-demo", help="Remove synthetic local demo systems and linked evidence.")
    clear_all_parser = subparsers.add_parser(
        "clear-all-local-data",
        help="Remove all application records from a non-production database.",
    )
    clear_all_parser.add_argument(
        "--confirm",
        choices=["CLEAR_ALL_LOCAL_DATA"],
        required=True,
        help="Required safety confirmation.",
    )
    args = parser.parse_args()

    if args.command == "init-db":
        init_db()
        print("Database initialized.")
        return

    with SessionLocal() as db:
        if args.command in {"seed-demo", "seed-showcase"}:
            created = seed_demo_systems(db)
            print(f"Showcase seed complete. Systems created: {created}.")
            return
        if args.command == "clear-demo":
            counts = clear_demo_data(db)
            print(f"Demo data cleared: {counts}.")
            return
        if args.command == "clear-all-local-data":
            settings = get_settings()
            if settings.app_env == "production":
                raise RuntimeError("clear-all-local-data cannot run when APP_ENV=production.")
            counts = clear_all_application_data(db)
            print(f"All local application data cleared: {counts}.")
            return


if __name__ == "__main__":
    main()
