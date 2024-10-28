# Checkmk extension for OPNsense

![build](https://github.com/scsitteam/checkmk_opnsense/workflows/build/badge.svg)
![flake8](https://github.com/scsitteam/checkmk_opnsense/workflows/Lint/badge.svg)
![pytest](https://github.com/scsitteam/checkmk_opnsense/workflows/pytest/badge.svg)

## Description

Checkmk Extensions to monitor [OPNsense](https://opnsense.org/) using the [API](https://docs.opnsense.org/development/api.html). The OPNsense Special Agent colltects data from the API enabling Checkmk to discover and monitor different aspects of OPNsense.

## Supported Check

* OPNsense Firmware - Checks if updates are available and ensurche updates have ben checked for.
* OPNsense Business - Checks the remaining runtime of the business license.
* CARP - Checks the status of CARP and the VirtualIPs.
* VirtualIP - Can be configured to discover and check the status of individual VirtualIPs. Optionaly groubed by Interface.
* Gateway - Checks status and monitoring of gateways with monitoring enabled.


## Development

For the best development experience use [VSCode](https://code.visualstudio.com/) with the [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension. This maps your workspace into a checkmk docker container giving you access to the python environment and libraries the installed extension has.

## Directories

The following directories in this repo are getting mapped into the Checkmk site.

$OMD_ROOT/local/lib/python3/cmk_addons/plugins/$PKGNAME

* `agent_based`, `graphing`, `lib`, `libexec`, `rulesets` and  `server_side_calls` are mapped into `local/lib/python3/cmk_addons/plugins/opnsense`

## Continuous integration
### Local

To build the package hit `Crtl`+`Shift`+`B` to execute the build task in VSCode.

`pytest` can be executed from the terminal or the test ui.

### Github Workflow

The provided Github Workflows run `pytest` and `flake8` in the same checkmk docker conatiner as vscode.
