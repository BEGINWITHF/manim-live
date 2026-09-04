"""LaTeX cache & media-cleanup helpers for real-time-manim.

While real-time-manim renders math, manim compiles each ``MathTex``/``Tex`` to an
SVG under ``<media_dir>/Tex``.  Re-running the same scene recompiles those SVGs
from scratch, which is slow and needs a working LaTeX toolchain every time.

These functions let an application **cache** those SVGs so unchanged math is
reused instead of recompiled, and **clean** the transient media folder the way
the demo runner used to.  They are the library versions of the helpers that
lived in ``run.py`` (``_restore_tex_cache`` / ``_save_tex_cache`` /
``_clean_media``); every path and behaviour is explicit so each caller controls
where the cache lives and how aggressive the cleanup is.

Typical use around a render::

    from real_time_manim.util import restore_tex_cache, save_tex_cache

    restore_tex_cache("tex_cache")     # warm manim's SVG dir from the cache
    ... run your scene(s) ...
    save_tex_cache("tex_cache")        # stash any newly compiled SVGs
"""
from __future__ import annotations

import os
import shutil
from typing import Iterable, Optional, Set


def _media_tex_dir(media_dir: Optional[str], tex_subdir: str) -> str:
    """Directory manim writes compiled LaTeX SVGs into.

    Defaults to ``<cwd>/media/Tex`` when ``media_dir`` is omitted.
    """
    base = media_dir if media_dir is not None else os.path.join(os.getcwd(), "media")
    return os.path.join(base, tex_subdir)


def _candidates(folder: str, only_ext: Set[str]) -> list:
    """Files in ``folder`` (if any) whose suffix is in ``only_ext``, sorted."""
    if not os.path.isdir(folder):
        return []
    if not only_ext:
        return sorted(f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)))
    return sorted(
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
        and os.path.splitext(f)[1].lower() in only_ext
    )


def _sync(src_dir: str, dst_dir: str, only_ext: Set[str],
          overwrite: bool, dry_run: bool, verbose: bool) -> int:
    """Copy new (or all, when ``overwrite``) matching files from src to dst.

    Returns the number of files that would be / were copied.
    """
    os.makedirs(dst_dir, exist_ok=True)
    done = 0
    for name in _candidates(src_dir, only_ext):
        target = os.path.join(dst_dir, name)
        if os.path.exists(target) and not overwrite:
            continue  # already cached/present -> skip
        if verbose and not dry_run:
            print(f"[cache] {'cp' if overwrite else 'add'} {os.path.basename(src_dir)}/{name} -> {dst_dir}")
        if not dry_run:
            shutil.copy2(os.path.join(src_dir, name), target)
        done += 1
    return done


def restore_tex_cache(cache_dir: str,
                      media_dir: Optional[str] = None,
                      *,
                      tex_subdir: str = "Tex",
                      only_ext: Iterable[str] = (".svg",),
                      overwrite: bool = False,
                      dry_run: bool = False,
                      verbose: bool = True) -> int:
    """Pre-populate manim's LaTeX SVG folder from a persistent cache.

    Copies cached SVGs into ``<media_dir>/<tex_subdir>`` so manim skips
    recompiling unchanged LaTeX on the next render.

    Parameters
    ----------
    cache_dir:
        Directory holding previously saved LaTeX SVGs (typically ``tex_cache``).
    media_dir:
        Root media folder; defaults to ``<cwd>/media``.
    tex_subdir:
        Sub-folder of ``media_dir`` manim compiles LaTeX into (default ``Tex``).
    only_ext:
        File extensions to treat as LaTeX assets (default ``.svg``).  Pass
        ``()`` to copy every file.
    overwrite:
        Also copy files already present in the destination (default ``False``
        only adds missing ones).
    dry_run:
        Report what would happen without copying anything.
    verbose:
        Print a line per copied file.

    Returns
    -------
    Number of files copied (or that would be copied in ``dry_run``).
    """
    return _sync(
        src_dir=cache_dir,
        dst_dir=_media_tex_dir(media_dir, tex_subdir),
        only_ext={e.lower() for e in only_ext},
        overwrite=overwrite,
        dry_run=dry_run,
        verbose=verbose,
    )


def save_tex_cache(cache_dir: str,
                   media_dir: Optional[str] = None,
                   *,
                   tex_subdir: str = "Tex",
                   only_ext: Iterable[str] = (".svg",),
                   overwrite: bool = False,
                   dry_run: bool = False,
                   verbose: bool = True) -> int:
    """Persist newly compiled LaTeX SVGs back into ``cache_dir``.

    New (or, with ``overwrite``, all) files in ``<media_dir>/<tex_subdir>`` are
    copied into ``cache_dir`` so the next run can restore them without
    recompiling.

    Parameters mirror :func:`restore_tex_cache`.  Returns the number of files
    saved (or that would be saved in ``dry_run``).
    """
    return _sync(
        src_dir=_media_tex_dir(media_dir, tex_subdir),
        dst_dir=cache_dir,
        only_ext={e.lower() for e in only_ext},
        overwrite=overwrite,
        dry_run=dry_run,
        verbose=verbose,
    )


def clear_media(media_dir: Optional[str] = None,
                *,
                verbose: bool = True) -> bool:
    """Remove manim's transient media output folder unconditionally.

    Unlike the cache helpers, clearing is never optional: this always attempts
    a full removal of the media folder, so callers cannot accidentally skip the
    cleanup that keeps the workspace tidy.

    Parameters
    ----------
    media_dir:
        Root media folder to delete; defaults to ``<cwd>/media``.
    verbose:
        Print the outcome.

    Returns
    -------
    ``True`` if the folder existed and was removed; ``False`` if it did not
    exist or could not be fully removed (e.g. a file is still locked by an open
    window).
    """
    base = media_dir if media_dir is not None else os.path.join(os.getcwd(), "media")
    if not os.path.isdir(base):
        if verbose:
            print(f"[clean] nothing to remove at {base}")
        return False
    try:
        shutil.rmtree(base)
        if verbose:
            print(f"[clean] removed {base}")
        return True
    except OSError:
        if verbose:
            print(f"[clean] could not remove {base} (files may be in use)")
        return False
