import shutil
import subprocess
import sys

standard_args = [
    "-strict-style",
    "-vet",
    "-vet-style",
    "-vet-semicolon",
    "-vet-cast",
    "-vet-semicolon",
    "-vet-shadowing",
    "-vet-style",
    "-vet-tabs",
    "-vet-unused",
    "-vet-unused-imports",
    "-vet-packages:qix",
    "-vet-unused-procedures",
    "-vet-unused-variables",
    "-vet-using-param",
    "-vet-using-stmt",
    "-warnings-as-errors",
]

debug_args = dict.fromkeys([*standard_args, "-o:none", "-debug"])
test_args = dict.fromkeys([*standard_args, *debug_args])
release_args = dict.fromkeys(
    [*standard_args, "-o:speed", "-disable-assert", "-no-bounds-check"]
)

asan_args = dict.fromkeys(
    [
        *standard_args,
        *debug_args,
        "-sanitize:address",
    ]
)

odin = shutil.which("odin")
if not odin:
    print("Please download odin and add it to your path:")
    print("  https://odin-lang.org/docs/install/")
    exit(1)

debug_build = ["build", ".", *debug_args.keys()]

targets = {
    "build": ("Builds the debug configuration", debug_build),
    "run": (
        "Builds and runs the debug configuration",
        ["run", ".", *debug_args.keys()],
    ),
    "debug": ("Builds the debug configuration", debug_build),
    "release": (
        "Builds the release (Optimized) configuration",
        ["build", ".", *release_args.keys()],
    ),
    "run-release": (
        "Builds and runs the release (Optimized) configuration",
        ["run", ".", *release_args.keys()],
    ),
    "test": ("Builds and runs the projects tests", ["test", ".", *test_args.keys()]),
    "asan": (
        "Builds the debug configuration with all sanitizers",
        ["build", ".", *asan_args.keys()],
    ),
    "test-asan": (
        "Builds the test configuration with all sanitizers",
        ["test", ".", *asan_args.keys()],
    ),
}

args = sys.argv
if len(args) > 1:
    build_arg = args[1]
    poll = targets.get(build_arg)
    max_target_len = max(len(target) for target in targets)

    if poll is None:
        print(f"Unknown build target: {build_arg}")
        for target, (description, _) in targets.items():
            print(f"  {target.ljust(max_target_len)} : {description}")
        exit(1)

    (_, flags) = poll
    command = str.join(" ", [odin, *flags])
    print(command)
    subprocess.run(command, shell=True)
else:
    command = str.join(" ", [odin, *debug_build])
    print(command)
    subprocess.run(command, shell=True)
