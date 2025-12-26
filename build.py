import os
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

version = "0.1.0"

python = sys.executable
exe_suffix = os.path.splitext(python)[1].endswith(".exe")
src_dir = "src"
binary = f"qix{'.exe' if exe_suffix else ''}"

README = "README.md"
CHANGELOG = "CHANGELOG.md"
LICENSE = "LICENSE"

assets = [README, CHANGELOG, LICENSE]

standard_args = [
    "-keep-executable",
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

msan_args = dict.fromkeys(
    [
        *standard_args,
        *debug_args,
        "-sanitize:memory",
    ]
)

odin = shutil.which("odin")
if not odin:
    print("Please download odin and add it to your path:")
    print("  https://odin-lang.org/docs/install/")
    exit(1)

odinfmt = shutil.which("odinfmt")
if not odinfmt:
    print("Please download ols, build odinfmt, and it to your path:")
    print("  https://github.com/DanielGavin/ols")

debug_path = os.path.join("bin", "debug")
debug_build = ["build", src_dir, *debug_args.keys()]

pack_targets = [
    ("qix-windows_amd64", True),
    ("qix-linux_amd64", False),
    ("qix-linux_arm64", False),
    ("qix-darwin_arm64", False),
    ("qix-darwin_amd64", False),
    ("qix-freebsd_amd64", False),
    ("qix-freebsd_arm64", False),
    ("qix-netbsd_amd64", False),
    ("qix-netbsd_arm64", False),
    ("qix-openbsd_amd64", False),
]

for target, _ in pack_targets:
    os.makedirs(os.path.join("pack", target), exist_ok=True)

targets = {
    "build": ("Builds the debug configuration", debug_build, debug_path),
    "run": (
        "Builds and runs the debug configuration",
        ["run", src_dir, *debug_args.keys()],
        debug_path,
    ),
    "debug": (
        "Builds the debug configuration",
        debug_build,
        debug_path,
    ),
    "release": (
        "Builds the release (Optimized) configuration",
        ["build", src_dir, *release_args.keys()],
        os.path.join("bin", "release"),
    ),
    "run-release": (
        "Builds and runs the release (Optimized) configuration",
        ["run", src_dir, *release_args.keys()],
        os.path.join("bin", "release"),
    ),
    "test": (
        "Builds and runs the projects tests",
        ["test", src_dir, *test_args.keys()],
        os.path.join("bin", "test"),
    ),
    "asan": (
        "Builds the debug configuration with address sanitizer",
        ["build", src_dir, *asan_args.keys()],
        os.path.join("bin", "asan"),
    ),
    "test-asan": (
        "Builds the test configuration with address sanitizer",
        ["test", src_dir, *asan_args.keys()],
        os.path.join("bin", "asan"),
    ),
    "msan": (
        "Builds the debug configuration with memory sanitizer",
        ["build", src_dir, *asan_args.keys()],
        os.path.join("bin", "msan"),
    ),
    "test-msan": (
        "Builds the test configuration with memory sanitizer",
        ["test", src_dir, *asan_args.keys()],
        os.path.join("bin", "msan"),
    ),
    "pack": (
        "Builds and packages all platform artifacts",
        ["build", src_dir, *release_args.keys()],
        os.path.join("pack"),
    ),
}

for _, _, root in targets.values():
    os.makedirs(root, exist_ok=True)

args = sys.argv
if len(args) > 1:
    build_arg = args[1]
    if odinfmt and build_arg == "fmt":
        for (parent, _, files) in os.walk(src_dir):
            for file in files:
                path = os.path.abspath(os.path.join(parent, file))
                command = str.join(" ", [odinfmt, f"-path:{path}", "-w"])
                subprocess.run(command, shell=True)
        exit(0)

    poll = targets.get(build_arg)
    max_target_len = max(len(target) for target in targets)

    if poll is None:
        print(f"Unknown build target: {build_arg}")
        for target, (description, _, _) in targets.items():
            print(f"  {target.ljust(max_target_len)} : {description}")
        exit(1)

    (_, flags, root) = poll
    if build_arg == "pack":
        for target, genzip in pack_targets:
            path = os.path.join(root, target)
            out = f"-out:{os.path.join(path, binary)}"
            command = str.join(" ", [odin, *flags, out])
            print(command)
            subprocess.run(command, shell=True)

            for asset in assets:
                dest = os.path.join(path, asset)
                shutil.copy(asset, dest)

            input_dir = Path(path)
            output_path = f"{target}-{version}"
            with tarfile.open(
                os.path.join("pack", f"{output_path}.tar.gz"), mode="w:gz"
            ) as tar:
                tar.add(input_dir, arcname=input_dir.name)

            if genzip:
                base_dir = input_dir.parent
                with zipfile.ZipFile(
                    os.path.join("pack", f"{output_path}.zip"),
                    mode="w",
                    compression=zipfile.ZIP_DEFLATED,
                ) as zipf:
                    for path in input_dir.rglob("*"):
                        arcname = path.relative_to(base_dir)
                        zipf.write(path, arcname)

        exit(0)

    out = f"-out:{os.path.join(root, binary)}"
    command = str.join(" ", [odin, *flags, out])
    print(command)
    subprocess.run(command, shell=True)
else:
    out = f"-out:{os.path.join(debug_path, binary)}"
    command = str.join(" ", [odin, *debug_build, out])
    print(command)
    subprocess.run(command, shell=True)
