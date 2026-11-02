[![black](https://github.com/cgs-earth/bascet/actions/workflows/black.yml/badge.svg)](https://github.com/cgs-earth/bascet/actions/workflows/black.yml)
[![tests](https://github.com/cgs-earth/bascet/actions/workflows/test.yml/badge.svg)](https://github.com/cgs-earth/bascet/actions/workflows/test.yml)

# bascet
bascet = BASic CEnsus Tables.

A way to easily grab some pre-formatted tables from the American Community Survey.

Attending Metaphysician: Margo Atkinson (matkinson@lincolninst.edu)

Examples with the Decennial Census and CPS forthcoming.

## Census API key
bascet downloads data from the Census Bureau API, which needs a free API key.
If you don't have one, request it here: https://api.census.gov/data/key_signup.html

Save your key once with `save_api_key()`:

```python
import bascet

bascet.save_api_key("your-census-api-key")
```

This does two things:
1. Writes `CENSUS_API_KEY="your-census-api-key"` to a `.env` file in your **current
   working directory** (creating the file if needed, or updating the key if it is
   already there).
2. Sets the `CENSUS_API_KEY` environment variable for the current Python session, so
   you can start downloading right away.

It returns the path of the `.env` file it wrote.

In later sessions you don't need to call it again: every download function looks up the
key automatically (via `get_api_key()`), first from the `CENSUS_API_KEY` environment
variable, then from a `.env` file in the current working directory or any of its
parent folders. So run your scripts or notebooks from the folder where you saved the
key (or one below it). If no key is found, you'll get a `KeyError` asking you to run
`save_api_key()`.

Other ways to provide the key:
- Set the `CENSUS_API_KEY` environment variable yourself.
- Copy [.env.example](https://github.com/cgs-earth/bascet/blob/main/.env.example) to
  `.env` and replace the placeholder with your key.
- Pass it directly to any download function with `api_key="..."`.

> **Keep your key private.** Don't commit your `.env` file. Add `.env` to your
> `.gitignore` if your project is in a git repository.

CGS GitHub Repository Best Practices Tracking:
1. Access: Currently Restricted, will be Public
2. Longevity: Continued Use
3. Target User: Novice (goal: pip install bascet)

Best Practices To Do:
- Code Coverage (e.g. testing)
