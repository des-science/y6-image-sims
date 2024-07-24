import subprocess

import click
from ruamel.yaml import YAML

yaml = YAML(typ="rt")
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.default_flow_style = False


def _reformat_lockfile(lockfile):
    # load / dump the lockfile to make sure it is sorted
    # so we get nice diffs
    with open(lockfile) as f:
        new_lock = yaml.load(f)
    new_lock["package"] = sorted(
        new_lock["package"], key=lambda x: (x["name"], x["platform"])
    )
    with open(lockfile, "w") as f:
        yaml.dump(new_lock, f)

    with open(lockfile) as f:
        lines = [line.rstrip() for line in f]

    with open(lockfile, "w") as f:
        f.write("\n".join(lines) + "\n")


@click.command()
@click.argument("envyaml", type=click.Path(exists=True))
@click.option(
    "--reformat-only", is_flag=True, help="Reformat the lockfile for nicer git diffs."
)
def main(envyaml, reformat_only):
    """(Re-)lock the conda environment given by ENVYAML and the corresponding .lock file."""

    lockfile = str(envyaml)[:-4] + "lock"
    print(f"Locking {envyaml} to {lockfile}", flush=True)

    if reformat_only:
        _reformat_lockfile(lockfile)
        return

    subprocess.run(
        ["conda", "lock", "--file", envyaml, "--lockfile", lockfile],
        check=True,
    )

    _reformat_lockfile(lockfile)


if __name__ == "__main__":
    main()
