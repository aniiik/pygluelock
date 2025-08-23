from pygluelock.glue_lock import GlueLock
import argparse
import asyncio

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument('--username', type=str, required=True, help='Input file path')
    parser.add_argument('--password', type=str, required=True, help='Output file path')
    return parser.parse_args()

def cli():
    asyncio.run(main())

async def main():
    args = parse_arguments()
    glue_lock = GlueLock(username=args.username, password=args.password)
    await glue_lock.connect()
    response = await glue_lock.get_all_locks()
    print(response)
    await glue_lock.close()

if __name__ == "__main__":
    cli()
