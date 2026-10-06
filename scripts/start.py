"""Start the configured Compose foundation with provider access disabled."""
import argparse
import subprocess
import environment
from readiness import ready
from smoke import require_offline_provider

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true')
    args = parser.parse_args()
    command = environment.compose() + ['up', '-d']
    if args.build:
        command.append('--build')
    subprocess.run(command, check=True)
    ready()
    require_offline_provider()
    print('All five services ready; provider access disabled.')

if __name__ == '__main__':
    main()
