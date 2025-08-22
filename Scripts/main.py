from pygluelock.glue_lock import GlueLock
import argparse
import asyncio

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument('--username', type=str, required=True, help='Input file path')
    parser.add_argument('--password', type=str, required=True, help='Output file path')
    return parser.parse_args()


async def main():
    args = parse_arguments()
    glue_lock = GlueLock(username=args.username, password=args.password)
    await glue_lock.connect()
    response = asyncio.run(glue_lock.toggle_lock())
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
