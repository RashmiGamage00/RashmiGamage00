# Publishing this profile

Everything in this folder belongs in **one special repository**. GitHub shows a
repository's README on your profile page only when the repository name matches
your username exactly.

Your username is **`RashmiGamage00`**, so the repository must be called
`RashmiGamage00` too. Not `rashmi-gamage`, not `profile`, not `README`.

> Your CV lists your GitHub as "Rashmi-Gamage". That is a different account
> owned by someone else, an electrical engineering graduate. Your account, the
> one holding Aqua-Assist, FlavourFeed, The Hotel and the supermarket system,
> is `RashmiGamage00`. Worth correcting on the CV before you send it anywhere.

## 1. Create the repository

1. Go to <https://github.com/new>
2. Repository name: `RashmiGamage00`
3. Make it **Public**
4. Tick **Add a README file** (it gets replaced in a moment)
5. Create. GitHub will show a note saying you found a secret. That is the right one.

## 2. Push the files

From this folder:

```bash
git init
git add .
git commit -m "Profile README"
git branch -M main
git remote add origin https://github.com/RashmiGamage00/RashmiGamage00.git
git push -u origin main --force
```

Or, if you would rather not use the command line: on the new repository page use
**Add file > Upload files**, drag in `README.md`, the `assets` folder, the
`scripts` folder and the `.github` folder, then commit. GitHub keeps the folder
structure when you drag folders in with Chrome.

Delete `SETUP.md` and `_preview.html` before pushing if you would rather they
were not public. Neither one hurts anything if you leave them.

## 3. Turn the two Actions on

Both live in `.github/workflows` and both need write access, which is off by
default on new accounts.

1. Repository **Settings > Actions > General**
2. Scroll to **Workflow permissions**
3. Choose **Read and write permissions**, then Save

Then run them once by hand so you do not have to wait for the schedule:

- **Actions > Refresh profile stat cards > Run workflow**
- **Actions > Generate contribution snake > Run workflow**

After the snake run finishes there will be a new `output` branch holding
`snake.svg`. That is what the README points at. Until then the snake shows as a
broken image, which is normal.

## 4. Two small things that make the profile look finished

**Your repositories have no descriptions.** The profile page shows them
underneath the README and they currently read as blank. Open each one, click the
gear next to About, and paste:

| Repository | Description |
| :-- | :-- |
| `AquaAssistDonationPlatform` | MERN platform for reporting water sanitation problems and backing clean water campaigns. Built the features, then ran the manual test passes over reporting and donations. |
| `FlavourFeedSocialMediaPlatformForFoodies` | Social platform for food reviewers, Spring Boot API with a React client. Built the post management module and tested create, edit and delete to the edges. |
| `TheHotelMobileApp` | Android app for booking event halls and rooms, backed by Firebase. Built the ratings and feedback feature with full CRUD, verified through Postman and Selenium. |
| `SuperMarketManagementSystem` | Online supermarket account management: registration, profiles and roles, with functional and usability testing automated in Selenium. |

**Your GitHub bio is empty.** Edit it from your profile page. Something like:

> QA Engineer at Convergence Lanka. Manual and automated testing, Postman, Selenium, Playwright. IEEE published on LoRa based wildfire detection.

## What is in here

| Path | What it does |
| :-- | :-- |
| `README.md` | The profile itself |
| `assets/banner.svg` | Animated header: wordmark, radar sweep, defect blips |
| `assets/coverage.svg` | Animated coverage meters by discipline |
| `assets/lifecycle.svg` | How a defect moves from found to verified |
| `assets/stats.svg` | GitHub numbers, redrawn daily by the Action |
| `assets/langs.svg` | Language mix, redrawn daily by the Action |
| `make-assets.py` | Regenerates the three hand drawn SVGs |
| `scripts/build_stats.py` | Fetches GitHub data and draws the two stat cards |
| `.github/workflows/stats.yml` | Runs the stats script every morning and commits the result |
| `.github/workflows/snake.yml` | Redraws the contribution grid as a snake |

To change the coverage percentages, the lifecycle wording or the banner text,
edit `make-assets.py` and run:

```bash
python make-assets.py
```

Nothing needs installing. Both scripts use the Python standard library only.

## Why the stat cards are self hosted

Almost every GitHub profile pulls its stat cards from three services:
`github-readme-stats`, `github-readme-activity-graph` and
`github-profile-trophy`. All three were checked while building this profile:

| Service | Response |
| :-- | :-- |
| `github-readme-stats.vercel.app` | `503` deployment paused |
| `github-readme-activity-graph.vercel.app` | `402` payment required |
| `github-profile-trophy.vercel.app` | `402` payment required |
| `streak-stats.demolab.com` | `200` working |
| `readme-typing-svg.demolab.com` | `200` working |
| `komarev.com` (view counter) | `200` working |
| `img.shields.io` | `200` working |

Anything pointing at the first three renders as a broken image right now, which
is why so many profiles look half finished. `scripts/build_stats.py` fetches the
same numbers straight from the GitHub API and draws them into `assets/`, so this
profile keeps working regardless of anyone else's hosting bill. The four
services that do work are still used, and if any of them goes down later the
only cost is one missing image.

## Two known cosmetic quirks

- **The Playwright badge has no icon.** Playwright is not in simple-icons, which
  is where shields.io gets its logos, so there is no icon to fetch. The badge is
  text only on purpose.
- **The LinkedIn icon is inlined.** simple-icons dropped the LinkedIn mark, so
  the glyph is embedded in the badge URL as a data URI. That long string in the
  README is intentional, do not tidy it away.

## If the animation does not move

GitHub serves README images through a proxy. SMIL animation inside SVG normally
survives it, but a proxy or a browser extension can flatten it. Every one of
these graphics is composed so that its first frame reads correctly on its own,
so a still version loses motion and nothing else.
