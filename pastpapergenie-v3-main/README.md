# pastpapergenie.co.uk

Plain HTML, CSS and JS. You don't need to run anything on your computer: GitHub builds the site for you.

## Put it online (all in the browser)
1. Make a repo and upload everything in this folder, including `.github/workflows/deploy.yml` and `CNAME`.
   If the `.github` folder won't upload, use Add file > Create new file, type `.github/workflows/deploy.yml` as the name and paste the contents.
2. Settings > Pages > Source: **GitHub Actions**.
3. Settings > Pages > Custom domain: `pastpapergenie.co.uk`, then tick Enforce HTTPS once it lets you.
4. At your domain registrar: four A records for `@` pointing to 185.199.108.153, 185.199.109.153, 185.199.110.153 and 185.199.111.153, and a CNAME for `www` pointing to `YOUR-USERNAME.github.io`.

Every time you commit a change, the Action rebuilds all the pages and redeploys. Check the Actions tab if something looks stale.

## Add a game
Edit `data/games.csv` on GitHub (pencil icon), add a row, commit. That's it.
- `mode`: `embed` shows another site's page in a sandboxed frame with no popups and no referrer. `hosted` plays files from `play/<slug>/index.html` in your repo. `link` and `pending` only appear on the Recommended page.
- Fill in `license`, `credit` and `source` from the real LICENSE file or the author's written yes. If you can't, leave the game out.
- `blurb` is the text on the game page. Use `||` between paragraphs and write it yourself.
- `img` (optional): a path like `assets/img/slug.png`.


## Notes
GitHub's docs give 1 GB as the recommended Pages size. Going past it has worked for some people, but GitHub can ask you to reduce it.
Pages can't send custom headers, which some WASM games need.
