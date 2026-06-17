# 7z Path Behavior Reference

7z resolves all paths relative to the current working directory (CWD) at the time of execution.

---

## Format Variants

| Input | Zip Entry | Notes |
|-------|-----------|-------|
| `install-it/conf` | `install-it\conf`, `...\settings.ini` | Full relative path stored |
| `./install-it/conf` | `conf`, `...\settings.ini` | **All components except last dropped (`install-it` removed)** |
| `./install-it/conf/` | `conf`, `...\settings.ini` | Same as above, trailing `/` stripped |
| `install-it/conf/` | `install-it\conf`, `...\settings.ini` | Trailing `/` stripped, full path kept |
| `../outside_cwd/other` | `other`, `...\outside.txt` | **`..` drops all resolved components except last; stores `other` (parent name dropped)** |
| `../../outside_cwd/other` | _(empty zip)_ | Path resolution failed — no common base |
| `subdir/child` | `subdir\child`, `...\file.txt` | Forward slash works |
| `subdir\child` | `subdir\child`, `...\file.txt` | Backslash works |

---

## Absolute Path Variants

| Input | Zip Entry | Notes |
|-------|-----------|-------|
| `C:\...\project\downloads` (abs inside CWD tree) | `downloads`, `...\amd.cat` | Common base stripped |
| `C:\...\outside_cwd\other` (abs outside CWD tree) | `other`, `...\outside.txt` | First component of relative portion dropped |
| `\\server\share\path` (UNC) | `other`, `...\outside.txt` | Same behavior as absolute path |
| `/usr/local/bin` (unix-style absolute) | _(empty zip)_ | Not recognized on Windows |

---

## Type Variants

| Input | Zip Entry | Notes |
|-------|-----------|-------|
| Single file `top.txt` | `top.txt` | Works |
| Directory with trailing slash `install-it/conf/` | `install-it\conf`, `...\settings.ini` | Trailing `/` normalized |
| Wildcard `*.ini` | _(nothing)_ | **No recursion — only CWD level matched** |
| Glob `wildcard_test/*.ini` | `wildcard_test\#hash.ini`, `a.ini`, `b.ini` | Wildcard works within specified dir |
| Nonexistent `this-does-not-exist` | _(empty zip)_ | Warning, non-zero exit, zip still created |
| Empty directory | _(empty)_ | Warning, directory not added |
| Path with spaces `wildcard_test/my file.txt` | `wildcard_test\my file.txt` | Works when properly passed |
| Special char `#hash.ini` | `wildcard_test\#hash.ini` | `#` treated as literal, not comment |

---

## Combination Variants

| Input | Zip Entry | Notes |
|-------|-----------|-------|
| `downloads` + abs path outside CWD | `downloads` tree + `other` tree | Both stored correctly |
| Overlapping `downloads` + `downloads/AMD` | `downloads` tree only | **Deduplicated — subdir already covered by parent** |
| Duplicate `install-it/conf` twice | **ERROR** | Non-zero exit, no zip created |
| File + parent dir `settings.ini` + `install-it/conf` | Full tree | Both included (parent includes file) |
| Duplicate file twice | **ERROR** | Same as duplicate dir |

---

## CWD Dependency

Same absolute path from different CWDs produces identical zip entries:

| CWD | Input | Zip Entry |
|-----|-------|-----------|
| `C:\project` | `C:\...\outside_cwd\other` | `other`, `...\outside.txt` |
| `C:\` (parent) | Same absolute path | `other`, `...\outside.txt` |
| `C:\Users\User\AppData\Local\Temp` | Same absolute path | `other`, `...\outside.txt` |

---

## Key Behaviors

1. **`./` prefix drops all components except the last.** `./a/b/c` stores as `c`, `./a/b` stores as `b`, `./a` stores as `a`.
2. **`../` prefix drops all components except the last.** `../outside_cwd/other` stores as `other`. But `..` alone stores the CWD name (not the resolved parent).
3. **Trailing `/` is normalized away.** No effect on stored path.
4. **Wildcard `*` does NOT recurse.** `*.ini` only matches files directly in CWD.
5. **Common base from CWD is always stripped.** Even absolute paths become relative to invocation directory.
6. **When target is outside CWD tree** — first component of the relative portion may also be dropped (7z quirk).
7. **Nonexistent paths** — warning + non-zero exit + empty zip still created.
8. **Duplicate paths specified twice** — ERROR, non-zero exit, no zip created.
9. **Hidden files** — included normally.
10. **`#` in filename** — treated as literal character, not comment.

---

## Practical Examples

```sh
# From C:\project, these produce different zip contents:
it-claws -z out.zip --zip-includes ./install-it/conf
# → zip contains: conf/ (first ./ component dropped)

it-claws -z out.zip --zip-includes install-it/conf
# → zip contains: install-it/conf/ (full path preserved)

it-claws -z out.zip --zip-includes ../sibling-dir
# → zip contains: sibling-dir/ (first .. component dropped)

# Multiple --zip-includes accumulate (each flag can have multiple values):
it-claws -z out.zip --zip-includes ./install-it/conf *.ini
# → zip contains: conf/ + any .ini files in CWD

# Overlapping paths are deduplicated:
it-claws -z out.zip --zip-includes install-it install-it/conf
# → zip contains: install-it/ only (child already covered by parent)
```

---

## it-claws Usage

```sh
# Include a config directory alongside downloads:
it-claws -o ./downloads -z ./driver-pack.zip --zip-includes install-it/conf

# Include multiple extra directories:
it-claws -o ./downloads -z ./driver-pack.zip --zip-includes install-it/conf scripts/startup

# Include files matching a pattern from CWD:
it-claws -o ./downloads -z ./driver-pack.zip --zip-includes "*.txt" install-it/conf
```

---

## Deep Nesting Variants

| Test | Input | Zip Entry | Notes |
|------|-------|-----------|-------|
| D1 | `a/b/c` (3 levels, dir has deeper children d/e/f) | `a\b\c` + all children | Recursive when dir has subdirs |
| D2 | `a/b/c/d` (4 levels) | `a\b\c\d` + children | Recursive |
| D3 | `a/b/c/d/e` (5 levels) | `a\b\c\d\e` + children | Recursive |
| D4 | `a/b/c/d/e/f` (6 levels, deepest) | `a\b\c\d\e\f`, `f.txt` | Works at any depth |
| D5 | `a/b/c` (no deeper children) | `a\b\c`, `c.txt` | Only contains actual contents |
| D7 | `./a/b/c` (3 levels with `./` prefix) | `c`, `c.txt` | **Drops all components except last (a and b)** |
| D8 | `./a/b` | `b`, `b.txt`, `b\c`, `b\c\c.txt` | Same — drops `a`, keeps `b` |
| D9 | `./a` | `a`, `a.txt`, `a\b`, `a\b\b.txt` | Only `.` stripped (one component total) |
| D10 | `a/b/c` (no prefix, for comparison) | `a\b\c`, `c.txt` | Full relative path preserved |
| D16 | `..` from `child` dir (parent is sibling) | `child` | **`..` drops first component of resolved path** |
| D17 | `..` from `grandchild` dir | `grandchild`, `gc.txt` | Same behavior |
| D21 | `../../../../..` (5 levels up from deep dir) | Scanned entire `C:\Users\User\AppData\Local\Temp` | **Too far up = scans entire parent tree** |
| D22 | `./a/b/c` vs `a/b/c` | `c` vs `a\b\c` | Confirms `./` drops exactly one component |

### Key deep-nesting behaviors

1. **Any depth works** — 7z handles 1 to 6+ levels identically, recursion is automatic.
2. **`./` drops all components except the last** — `./a/b/c` → `c`, `./a/b` → `b`, `./a` → `a`.
3. **`..` behavior is more complex:**
   - `..` alone stores the CWD name (regardless of where it points in filesystem)
   - `..\subdir` only works if `subdir` exists inside the resolved target of `..`
   - Each `..` drops one component of the full resolved path
4. **`..` can reach too far** — going 5+ levels up from a deep structure can scan entire parent tree (warning: slow, large zip).
5. **No limit on depth** — tested up to 6 levels, confirmed working.