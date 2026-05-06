# Releasing AareTempBar

1. Update the version in `pyproject.toml` and `AareTempBar.spec`.
2. Commit and push.
3. Tag the release: `git tag v0.9.0`
4. Push the tag: `git push origin v0.9.0`
5. GitHub Actions builds the `.app` with PyInstaller, zips it, and attaches it to a release.
6. After the CI finishes, copy the SHA256 of `AareTempBar-macos.zip` from the release page.
7. Update the Cask in `jl115/homebrew-aare` with the new version and SHA256.
8. Run `brew bump-cask-pr aare-temp-menubar` (or edit manually).

## Local Build

```bash
uv sync
./scripts/build_app.sh
open dist/AareTempBar.app
```

Because the app is ad-hoc signed, macOS may warn about an unidentified developer on first launch. Right-click the app in Finder and choose **Open** to bypass the warning.
