from dailyGeneric import start_generic_posting, TypeOfPost
from dailyConfig import ACCOUNTS
from dailyGeneric import TypeOfPost
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

def run_daily_script(account_name: str, action_to_do: TypeOfPost):
    # Run the daily.py script with the specified account and action
    account = ACCOUNTS.get(account_name)
    if not account:
        print(f"Error: Account '{account_name}' not found in config.")
        return

    # Start posting for the given account
    start_generic_posting(
        account["BLUESKY_HANDLE"],
        account["BLUESKY_PASSWORD"],
        account["FILE_NAME"],
        account["HASHTAGS"],
        action_to_do
    )

def main(action_to_do: TypeOfPost):
    # Run the daily script for all accounts
    for account_name in ACCOUNTS:
        run_daily_script(account_name, action_to_do)

if __name__ == '__main__':
    import sys
    
    # Get the action type from the command-line argument, default to RANDOM if none is provided
    action_arg = sys.argv[1] if len(sys.argv) > 1 else "RANDOM"
    action_to_do = TypeOfPost[action_arg.upper()]  # Convert argument to TypeOfPost
    
    main(action_to_do)
