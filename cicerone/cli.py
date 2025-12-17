import click


@click.group()
def cli_group():
    """
    Cicerone:  Explore OpenAPI schemas, the Pythonic way
    https://github.com/phalt/cicerone
    """


@click.command()
def version():
    """
    Print the current version of cicerone
    """
    from cicerone import settings

    print(f"cicerone {settings.VERSION}")


cli_group.add_command(version)


if __name__ == "__main__":
    cli_group()
