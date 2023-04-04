# Github Actions Deprecation Finder

This will do the following:

- Check each repo, if it has a `.github/workflows` move on to the next step
- Check it has either a `yaml` or `yml` files in `.github/workflows`
- Download the workflow file to `temp-workflow.yml`
- Check for deprecations defined in the config file

## Usage

Please ensure you have the following ENVVARS set:

```
# Your PAT Token with Full Repo Access
export GH_ACCESS_TOKEN="ghp_xxxxxxxxxxxxxxx"
# Your GH Org name
export GH_ORG="my_org"
```

You can set them via options on the commands, but for best practice they should be set in your ENV.


## Examples

```
github-deprecation-finder find "infra-splat"
```

```
github-deprecation-finder find-all
```

## Help
Please run `github-deprecation-finder --help` to see all the commands and options.