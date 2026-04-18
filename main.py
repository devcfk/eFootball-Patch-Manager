import argparse

from patch_manager.ui.app import PatchManagerApp


def run() -> None:
    parser = argparse.ArgumentParser(description="eFootball Patch Manager")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Mode test : simule toutes les opérations sans modifier les fichiers du jeu",
    )
    args = parser.parse_args()

    app = PatchManagerApp(test_mode=args.test)
    app.mainloop()


if __name__ == "__main__":
    run()
