# Harness startup, watchdogs and input

## Confirm the harness actually starts

Godot engine flags, including `--script`, belong before `--`. Only game or harness arguments belong after it. Resolve the script in the current repository. For example, adapt this shape to the project's actual paths:

```sh
godot --headless --path . --script res://tests/acceptance/world_acceptance.gd -- --scenario=maximum
```

Moving `--script` after `--` can launch the ordinary game indefinitely; that is not evidence of a render hang. Require an identifying start message, explicit final pass or fail and meaningful exit status. An import, parser/build failure, process exit or absence of error text is not acceptance. Parser-negative fixtures must assert their intended diagnostic and status rather than any nonzero exit.

For long tests, emit concise phase progress and enforce a wall-clock limit as well as any frame limit. A bare GDScript assertion can stop its coroutine without quitting `SceneTree`; keep the watchdog independent and make failure exit explicitly. On timeout record the last phase, scenario dimensions, ready or pending work and process status. Terminate only the exact test process created by the run.

Latch failure before requesting exit. Every later evidence, PASS and success-exit path must respect that latch, including a coroutine resumed after timeout. Exercise an intentionally stopped coroutine and require timeout failure with no PASS.

## Make viewport and input delivery explicit

On macOS, a headless hidden window can still report 64×64 after an attempted resize. Establish the virtual viewport with `content_scale_size` and `Window.CONTENT_SCALE_MODE_VIEWPORT` before projecting pointer rays, then assert the visible rectangle. Keep this as a platform-specific check rather than a universal engine requirement.

For synthetic gestures in that viewport, consider `Viewport.push_input(event, true)` and `notify_mouse_entered()` instead of assuming window-coordinate injection matches projection. The [official Viewport API](https://docs.godotengine.org/en/stable/classes/class_viewport.html#class-viewport-method-push-input) defines local coordinates and normal event propagation. Check the actual consumer because this is not equivalent to all global `Input` polling or project remapping. Keep real handlers and picking active; direct begin, finish or commit calls are not input evidence.

Set camera distance, clipping, zoom and presentation origin for the scenario size. A small default camera is not a maximum-map setup. Rust world coordinates remain authoritative; presentation centering must be consistent across picking, markers, terrain and overlays.
