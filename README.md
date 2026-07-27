# OPI generation for CS-Studio and Phoebus

This repository is forked from [dls-controls/cssgen](https://github.com/dls-controls/cssgen/blob/master/README.md), and renamed to `opi-generator`, with the package name of `opigen`.

After a thorough refactoring process, `opigen` now supports OPI files generation for both CS-Studio and Phoebus from the same script, which minimizes the effort required to maintain both platforms, making it more efficient and streamlined.

## Installation

```
pip install opigen
```

## Attribute Mapping

`opigen` can generate OPI files that are compatible with both CS-Studio and Phoebus by utilizing the concept of "attribute mapping". Essentially, this involves ensuring that each attribute of a widget class in CS-Studio has a corresponding counterpart in Phoebus. By accurately mapping the attribute names, `opigen` can seamlessly handle both systems with the same code. This approach not only simplifies the development process but also ensures cross-compatibility, making it easier for developers to create robust and adaptable OPI files that can be used across different platforms.

The command line tool `opigen-export_attr_map` could be used to export
the attribute map from CS-Studio (.opi) to Phoebus (.bob) that are in-use.

The exported file contains an attribute map from CS-Studio (`.opi`) to Phoebus (`.bob`).

The attribute name must be mapped for Phoebus, otherwise it will be
missing in the generated file.

Let's assume an use-case that `bitReverse` attribute of the class `Byte` (refers to
`ByteMonitor`) needs to be correctly handled
on both, but the system deployed attribute map does not provide it, the use will
have to extend it. To extend or update it, follow these steps:

- Create a file named `attr.toml` in the current working directory.
- Create a new section with the widget class name, e.g. `[Byte]`.
- Add new attribute maps or override existing ones under the new section,
  e.g. `bitReverse = "bitReverse"`.
- If there is no `attr.toml` in the current working directory,
  use the one in the user home directory at `~/.opigen/attr.toml` to do
  the extend or override if possible.
- If `attr.toml` exists in both places, the one in the current working
  directory takes precedence.

## Global Formatting

`opigen` provides global formatting options through `opigen/config/color.def` and `opigen/config/font.def`.

The module searches for `*.def` in the following order:

1. `cwd/*.def`
2. `~/.opigen/*.def`
3. `<opigen-package-dir>/config/*.def`

## Development

- Formatter: `yapf`
