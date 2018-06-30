import click

from commands import dotnet, python

SUPPORTED = {'dotnet': '.NET',
             'python': 'Python',
             }


@click.command()
@click.option('--language', '-l', type=click.Choice(
              [k for k, v in SUPPORTED.items()]))
# TODO: add option/flag to include or not include prereleases
def main(language):
    """
    Vervet requests package version history from package managers and
    prints the response to file.
    """
    language_title = SUPPORTED[language]

    if language == 'dotnet':
        filename = dotnet.dotnet()
    if language == 'python':
        filename = python.python()

    print("Vetting package versions...")
    print("{} package versions saved to {}.\n".format(
          language_title, filename))


if __name__ == '__main__':
    main()
