#!/usr/bin/env python3
"""WTACMI minimal recorder.

Records War Thunder localhost telemetry plus local keyboard/mouse input inferred
from a user-selected War Thunder controls .blk file.
"""

import argparse
import ctypes
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
import zipfile
from typing import Callable, Dict, Iterable, List, Optional, Tuple


APP_VERSION = "0.1.0"
FORMAT_VERSION = 1
DEFAULT_BASE_URL = "http://localhost:8111"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
DEFAULT_TELEMETRY_HZ = 20.0
DEFAULT_INPUT_HZ = 60.0
DEFAULT_MAP_OBJECTS_HZ = 5.0

HIGH_RATE_ENDPOINTS = {
    "state": "/state",
    "indicators": "/indicators",
}

STATIC_ENDPOINTS = {
    "map_info": "/map_info.json",
    "mission": "/mission.json",
}

LOW_RATE_ENDPOINTS = {
    "map_objects": "/map_obj.json",
}

DEFAULT_ENDPOINTS = {
    **HIGH_RATE_ENDPOINTS,
    **STATIC_ENDPOINTS,
    **LOW_RATE_ENDPOINTS,
}

CONTROL_BINDING_KEYS = {
    "pitch_up": ["elevator_rangeMin"],
    "pitch_down": ["elevator_rangeMax"],
    "roll_left": ["ailerons_rangeMin"],
    "roll_right": ["ailerons_rangeMax"],
    "throttle_up": ["throttle_rangeMax"],
    "throttle_down": ["throttle_rangeMin"],
    "flaps": ["ID_FLAPS"],
    "flaps_up": ["ID_FLAPS_UP"],
    "flaps_down": ["ID_FLAPS_DOWN"],
    "airbrake": ["ID_AIR_BRAKE"],
    "fire_primary": ["ID_FIRE_PRIMARY", "ID_FIRE_GM", "ID_FIRE_PRIMARY_HELICOPTER"],
    "fire_secondary": ["ID_FIRE_SECONDARY", "ID_FIRE_SECONDARY_HELICOPTER"],
    "weapon_lock": ["ID_WEAPON_LOCK", "ID_LOCK_TARGET", "ID_LOCK_TARGETING"],
    "countermeasures": [
        "ID_FLARES",
        "ID_COUNTERMEASURES_FLARES",
        "ID_COUNTERMEASURES_CHAFF",
    ],
}

# War Thunder .blk keyboardKey values are DirectInput scan codes. GetAsyncKeyState
# needs Windows virtual-key codes, so keep the conversion explicit.
DIK_TO_VK = {
    1: 0x1B,
    2: ord("1"),
    3: ord("2"),
    4: ord("3"),
    5: ord("4"),
    6: ord("5"),
    7: ord("6"),
    8: ord("7"),
    9: ord("8"),
    10: ord("9"),
    11: ord("0"),
    12: 0xBD,
    13: 0xBB,
    14: 0x08,
    15: 0x09,
    16: ord("Q"),
    17: ord("W"),
    18: ord("E"),
    19: ord("R"),
    20: ord("T"),
    21: ord("Y"),
    22: ord("U"),
    23: ord("I"),
    24: ord("O"),
    25: ord("P"),
    26: 0xDB,
    27: 0xDD,
    28: 0x0D,
    29: 0xA2,
    30: ord("A"),
    31: ord("S"),
    32: ord("D"),
    33: ord("F"),
    34: ord("G"),
    35: ord("H"),
    36: ord("J"),
    37: ord("K"),
    38: ord("L"),
    39: 0xBA,
    40: 0xDE,
    41: 0xC0,
    42: 0xA0,
    43: 0xDC,
    44: ord("Z"),
    45: ord("X"),
    46: ord("C"),
    47: ord("V"),
    48: ord("B"),
    49: ord("N"),
    50: ord("M"),
    51: 0xBC,
    52: 0xBE,
    53: 0xBF,
    54: 0xA1,
    55: 0x6A,
    56: 0xA4,
    57: 0x20,
    58: 0x14,
    59: 0x70,
    60: 0x71,
    61: 0x72,
    62: 0x73,
    63: 0x74,
    64: 0x75,
    65: 0x76,
    66: 0x77,
    67: 0x78,
    68: 0x79,
    69: 0x90,
    70: 0x91,
    71: 0x67,
    72: 0x68,
    73: 0x69,
    74: 0x6D,
    75: 0x64,
    76: 0x65,
    77: 0x66,
    78: 0x6B,
    79: 0x61,
    80: 0x62,
    81: 0x63,
    82: 0x60,
    83: 0x6E,
    87: 0x7A,
    88: 0x7B,
    156: 0x0D,
    157: 0xA3,
    181: 0x6F,
    183: 0x2C,
    184: 0xA5,
    197: 0x13,
    199: 0x24,
    200: 0x26,
    201: 0x21,
    203: 0x25,
    205: 0x27,
    207: 0x23,
    208: 0x28,
    209: 0x22,
    210: 0x2D,
    211: 0x2E,
}

MOUSE_BUTTON_TO_VK = {
    0: 0x01,
    1: 0x02,
    2: 0x04,
    3: 0x05,
    4: 0x06,
}

KEY_NAME = {
    0x01: "MouseLeft",
    0x02: "MouseRight",
    0x04: "MouseMiddle",
    0x05: "MouseX1",
    0x06: "MouseX2",
    0x08: "Backspace",
    0x09: "Tab",
    0x0D: "Enter",
    0x14: "CapsLock",
    0x1B: "Esc",
    0x20: "Space",
    0x21: "PageUp",
    0x22: "PageDown",
    0x23: "End",
    0x24: "Home",
    0x25: "Left",
    0x26: "Up",
    0x27: "Right",
    0x28: "Down",
    0x2C: "PrintScreen",
    0x2D: "Insert",
    0x2E: "Delete",
    0x70: "F1",
    0x71: "F2",
    0x72: "F3",
    0x73: "F4",
    0x74: "F5",
    0x75: "F6",
    0x76: "F7",
    0x77: "F8",
    0x78: "F9",
    0x79: "F10",
    0x7A: "F11",
    0x7B: "F12",
    0x90: "NumLock",
    0x91: "ScrollLock",
    0xA0: "LeftShift",
    0xA1: "RightShift",
    0xA2: "LeftCtrl",
    0xA3: "RightCtrl",
    0xA4: "LeftAlt",
    0xA5: "RightAlt",
    0xBA: ";",
    0xBB: "=",
    0xBC: ",",
    0xBD: "-",
    0xBE: ".",
    0xBF: "/",
    0xC0: "`",
    0xDB: "[",
    0xDC: "\\",
    0xDD: "]",
    0xDE: "'",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


def default_output_path() -> str:
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return os.path.join(DEFAULT_OUTPUT_DIR, f"recording-{timestamp}.acmi")


def monotonic_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000.0, 3)


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def vk_label(vk: int) -> str:
    if 0x30 <= vk <= 0x39 or 0x41 <= vk <= 0x5A:
        return chr(vk)
    if 0x60 <= vk <= 0x69:
        return f"Num{vk - 0x60}"
    if vk in KEY_NAME:
        return KEY_NAME[vk]
    return f"VK_{vk}"


def parse_blk_bindings(path: str) -> Dict[str, List[Dict[str, object]]]:
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        text = handle.read()

    bindings: Dict[str, List[Dict[str, object]]] = {}
    block_re = re.compile(r"^\s*([A-Za-z0-9_]+)\s*\{", re.MULTILINE)
    for match in block_re.finditer(text):
        name = match.group(1)
        start = match.end()
        depth = 1
        pos = start
        while pos < len(text) and depth:
            if text[pos] == "{":
                depth += 1
            elif text[pos] == "}":
                depth -= 1
            pos += 1
        body = text[start : pos - 1]
        keyboard_codes = [int(v) for v in re.findall(r"keyboardKey:i=(-?\d+)", body)]
        mouse_buttons = [int(v) for v in re.findall(r"mouseButton:i=(-?\d+)", body)]
        if not keyboard_codes and not mouse_buttons:
            continue
        keys = []
        unsupported = []
        for code in keyboard_codes:
            vk = DIK_TO_VK.get(code)
            if vk is None:
                unsupported.append({"kind": "keyboard", "code": code})
            else:
                keys.append({"kind": "keyboard", "sourceCode": code, "vk": vk, "label": vk_label(vk)})
        for button in mouse_buttons:
            vk = MOUSE_BUTTON_TO_VK.get(button)
            if vk is None:
                unsupported.append({"kind": "mouse", "code": button})
            else:
                keys.append({"kind": "mouse", "sourceCode": button, "vk": vk, "label": vk_label(vk)})
        bindings.setdefault(name, []).append({"keys": keys, "unsupported": unsupported})
    return bindings


def select_control_bindings(raw_bindings: Dict[str, List[Dict[str, object]]]) -> Dict[str, List[Dict[str, object]]]:
    selected: Dict[str, List[Dict[str, object]]] = {}
    for control_name, blk_names in CONTROL_BINDING_KEYS.items():
        alternatives: List[Dict[str, object]] = []
        for blk_name in blk_names:
            for binding in raw_bindings.get(blk_name, []):
                alternatives.append({"blkName": blk_name, **binding})
        selected[control_name] = alternatives
    return selected


class InputSampler:
    def __init__(self, control_bindings: Dict[str, List[Dict[str, object]]]):
        self.control_bindings = control_bindings
        if os.name == "nt":
            self._get_async_key_state = ctypes.windll.user32.GetAsyncKeyState
        else:
            self._get_async_key_state = None

    def is_pressed(self, vk: int) -> bool:
        if self._get_async_key_state is None:
            return False
        return bool(self._get_async_key_state(vk) & 0x8000)

    def binding_pressed(self, binding: Dict[str, object]) -> bool:
        keys = binding.get("keys") or []
        if not keys:
            return False
        return all(self.is_pressed(int(key["vk"])) for key in keys)

    def sample(self) -> Dict[str, object]:
        controls: Dict[str, object] = {}
        active_bindings: Dict[str, List[str]] = {}

        for control_name, alternatives in self.control_bindings.items():
            labels = []
            pressed = False
            for binding in alternatives:
                if self.binding_pressed(binding):
                    pressed = True
                    labels.append("+".join(str(key["label"]) for key in binding["keys"]))
            controls[control_name] = pressed
            if labels:
                active_bindings[control_name] = labels

        controls["pitch"] = float(controls.get("pitch_down", False)) - float(controls.get("pitch_up", False))
        controls["roll"] = float(controls.get("roll_right", False)) - float(controls.get("roll_left", False))
        controls["throttle_step"] = float(controls.get("throttle_up", False)) - float(controls.get("throttle_down", False))

        return {"controls": controls, "activeBindings": active_bindings}


class TelemetryClient:
    def __init__(self, base_url: str, timeout: float):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def fetch_json(self, path: str) -> Tuple[Optional[object], float, Optional[str]]:
        url = self.base_url + path
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
            latency_ms = round((time.perf_counter() - start) * 1000.0, 3)
            return json.loads(body), latency_ms, None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            latency_ms = round((time.perf_counter() - start) * 1000.0, 3)
            return None, latency_ms, str(exc)


def benchmark_telemetry_rate(
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 0.25,
    duration: float = 3.0,
    endpoints: Optional[Dict[str, str]] = None,
) -> Dict[str, object]:
    """Estimate the fastest high-rate telemetry cycle for this machine/game state."""
    endpoint_map = endpoints or HIGH_RATE_ENDPOINTS
    client = TelemetryClient(base_url, timeout)
    started = time.perf_counter()
    cycle_durations: List[float] = []
    endpoint_latencies: Dict[str, List[float]] = {name: [] for name in endpoint_map}
    errors: Dict[str, int] = {name: 0 for name in endpoint_map}
    cycles = 0
    successful_cycles = 0

    while time.perf_counter() - started < duration:
        cycle_started = time.perf_counter()
        cycle_success = True
        for name, endpoint in endpoint_map.items():
            _data, latency_ms, error = client.fetch_json(endpoint)
            endpoint_latencies[name].append(latency_ms)
            if error:
                errors[name] += 1
                cycle_success = False
        cycle_durations.append((time.perf_counter() - cycle_started) * 1000.0)
        cycles += 1
        if cycle_success:
            successful_cycles += 1

    elapsed = max(time.perf_counter() - started, 0.001)
    full_cycle_hz = cycles / elapsed
    successful_cycle_hz = successful_cycles / elapsed
    avg_cycle_ms = sum(cycle_durations) / len(cycle_durations) if cycle_durations else 0.0
    sorted_cycle = sorted(cycle_durations)
    p95_index = min(len(sorted_cycle) - 1, int(len(sorted_cycle) * 0.95)) if sorted_cycle else 0
    p95_cycle_ms = sorted_cycle[p95_index] if sorted_cycle else 0.0
    recommended_hz = max(1.0, min(120.0, successful_cycle_hz * 0.7 if successful_cycles else full_cycle_hz * 0.5))

    endpoint_summary = {}
    for name, values in endpoint_latencies.items():
        endpoint_summary[name] = {
            "avgLatencyMs": round(sum(values) / len(values), 3) if values else None,
            "maxLatencyMs": round(max(values), 3) if values else None,
            "errors": errors[name],
        }

    return {
        "durationSec": round(elapsed, 3),
        "cycles": cycles,
        "successfulCycles": successful_cycles,
        "fullCycleHz": round(full_cycle_hz, 2),
        "successfulCycleHz": round(successful_cycle_hz, 2),
        "avgCycleMs": round(avg_cycle_ms, 3),
        "p95CycleMs": round(p95_cycle_ms, 3),
        "recommendedHz": round(recommended_hz, 1),
        "endpoints": endpoint_summary,
    }


def write_json_line(handle, value: Dict[str, object]) -> None:
    handle.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")
    handle.flush()


def build_manifest(args, recording_id: str, started_at: str, bindings: Dict[str, List[Dict[str, object]]]) -> Dict[str, object]:
    return {
        "formatVersion": FORMAT_VERSION,
        "appVersion": APP_VERSION,
        "recordingId": recording_id,
        "pilotAlias": args.pilot,
        "createdAtUtc": started_at,
        "clock": {
            "type": "monotonic",
            "startWallTimeUtc": started_at,
        },
        "sampleRates": {
            "telemetryHzTarget": args.telemetry_hz,
            "mapObjectsHzTarget": args.map_objects_hz,
            "inputHzTarget": args.input_hz,
        },
        "source": {
            "localhostBaseUrl": args.base_url,
            "endpoints": DEFAULT_ENDPOINTS,
            "endpointGroups": {
                "highRate": HIGH_RATE_ENDPOINTS,
                "lowRate": LOW_RATE_ENDPOINTS,
                "static": STATIC_ENDPOINTS,
            },
            "localhostDocumentation": "https://github.com/lucasvmx/WarThunder-localhost-documentation",
        },
        "controlsFile": {
            "path": os.path.abspath(args.controls),
            "sha256": sha256_file(args.controls),
        },
        "inputBindings": bindings,
    }


def record_endpoint(
    telemetry_client: TelemetryClient,
    telemetry_file,
    errors_file,
    t_ms: float,
    name: str,
    endpoint: str,
) -> None:
    data, latency_ms, error = telemetry_client.fetch_json(endpoint)
    record = {
        "tMs": t_ms,
        "endpointName": name,
        "endpoint": endpoint,
        "latencyMs": latency_ms,
    }
    if error is None:
        record["data"] = data
        write_json_line(telemetry_file, record)
    else:
        write_json_line(
            errors_file,
            {**record, "source": "telemetry-poller", "severity": "warning", "message": error},
        )


def write_package(temp_dir: str, output_path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for name in ["manifest.json", "telemetry.ndjson", "inputs.ndjson", "events.ndjson", "errors.ndjson"]:
            path = os.path.join(temp_dir, name)
            if os.path.exists(path):
                package.write(path, arcname=name)


def summarize_bindings(bindings: Dict[str, List[Dict[str, object]]]) -> Iterable[str]:
    for control_name, alternatives in bindings.items():
        labels = []
        for binding in alternatives:
            keys = binding.get("keys") or []
            if keys:
                labels.append("+".join(str(key["label"]) for key in keys))
        yield f"{control_name}: {', '.join(labels) if labels else 'unbound'}"


def run_recording(
    args,
    should_stop: Optional[Callable[[], bool]] = None,
    log: Callable[[str], None] = print,
) -> int:
    raw_bindings = parse_blk_bindings(args.controls)
    control_bindings = select_control_bindings(raw_bindings)
    input_sampler = InputSampler(control_bindings)
    telemetry_client = TelemetryClient(args.base_url, args.timeout)

    recording_id = str(uuid.uuid4())
    started_at = utc_now()
    temp_dir = tempfile.mkdtemp(prefix="wtacmi-recording-")

    manifest = build_manifest(args, recording_id, started_at, control_bindings)
    with open(os.path.join(temp_dir, "manifest.json"), "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)

    log("WTACMI recorder")
    log(f"controls: {os.path.abspath(args.controls)}")
    log(f"output:   {os.path.abspath(args.output)}")
    log("selected bindings:")
    for line in summarize_bindings(control_bindings):
        log(f"  {line}")
    log("press Ctrl+C or Stop to stop recording")

    start = time.perf_counter()
    next_input = start
    next_telemetry = start
    next_map_objects = start
    telemetry_interval = 1.0 / args.telemetry_hz
    input_interval = 1.0 / args.input_hz
    map_objects_interval = 1.0 / args.map_objects_hz if args.map_objects_hz > 0 else None
    stop_at = start + args.duration if args.duration else None

    try:
        with open(os.path.join(temp_dir, "telemetry.ndjson"), "a", encoding="utf-8") as telemetry_file, open(
            os.path.join(temp_dir, "inputs.ndjson"), "a", encoding="utf-8"
        ) as inputs_file, open(os.path.join(temp_dir, "events.ndjson"), "a", encoding="utf-8") as events_file, open(
            os.path.join(temp_dir, "errors.ndjson"), "a", encoding="utf-8"
        ) as errors_file:
            write_json_line(events_file, {"tMs": 0, "type": "recording-started", "utc": started_at})
            for name, endpoint in STATIC_ENDPOINTS.items():
                record_endpoint(telemetry_client, telemetry_file, errors_file, 0, name, endpoint)

            while True:
                now = time.perf_counter()
                if stop_at and now >= stop_at:
                    break
                if should_stop and should_stop():
                    break

                if now >= next_input:
                    sample = input_sampler.sample()
                    sample["tMs"] = monotonic_ms(start)
                    write_json_line(inputs_file, sample)
                    next_input += input_interval

                if now >= next_telemetry:
                    t_ms = monotonic_ms(start)
                    for name, endpoint in HIGH_RATE_ENDPOINTS.items():
                        record_endpoint(telemetry_client, telemetry_file, errors_file, t_ms, name, endpoint)
                    next_telemetry += telemetry_interval

                if map_objects_interval is not None and now >= next_map_objects:
                    t_ms = monotonic_ms(start)
                    for name, endpoint in LOW_RATE_ENDPOINTS.items():
                        record_endpoint(telemetry_client, telemetry_file, errors_file, t_ms, name, endpoint)
                    next_map_objects += map_objects_interval

                next_times = [next_input, next_telemetry]
                if map_objects_interval is not None:
                    next_times.append(next_map_objects)
                sleep_for = min(next_times) - time.perf_counter()
                if sleep_for > 0:
                    time.sleep(min(sleep_for, 0.01))
    except KeyboardInterrupt:
        log("\nstopping...")
    finally:
        with open(os.path.join(temp_dir, "events.ndjson"), "a", encoding="utf-8") as events_file:
            write_json_line(events_file, {"tMs": monotonic_ms(start), "type": "recording-stopped", "utc": utc_now()})
        write_package(temp_dir, args.output)
        shutil.rmtree(temp_dir, ignore_errors=True)

    log(f"saved {os.path.abspath(args.output)}")
    return 0


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record War Thunder 8111 telemetry and local input into a .acmi file.")
    parser.add_argument("--controls", required=True, help="Path to War Thunder controls .blk file.")
    parser.add_argument("--output", default=default_output_path(), help="Output .acmi package path.")
    parser.add_argument("--pilot", default=os.environ.get("USERNAME", "Pilot"), help="Pilot alias stored in the manifest.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="War Thunder localhost telemetry base URL.")
    parser.add_argument("--telemetry-hz", type=float, default=DEFAULT_TELEMETRY_HZ, help="High-rate /state and /indicators polling rate.")
    parser.add_argument("--map-objects-hz", type=float, default=DEFAULT_MAP_OBJECTS_HZ, help="/map_obj.json polling rate. Use 0 to disable.")
    parser.add_argument("--input-hz", type=float, default=DEFAULT_INPUT_HZ, help="Input sampling rate.")
    parser.add_argument("--timeout", type=float, default=0.25, help="HTTP timeout per endpoint in seconds.")
    parser.add_argument("--duration", type=float, default=0.0, help="Optional recording duration in seconds. 0 records until Ctrl+C.")
    args = parser.parse_args(argv)

    if args.telemetry_hz <= 0:
        parser.error("--telemetry-hz must be greater than 0")
    if args.input_hz <= 0:
        parser.error("--input-hz must be greater than 0")
    if args.map_objects_hz < 0:
        parser.error("--map-objects-hz must be 0 or greater")
    if args.timeout <= 0:
        parser.error("--timeout must be greater than 0")
    if not os.path.isfile(args.controls):
        parser.error(f"--controls does not exist: {args.controls}")
    if not args.output.lower().endswith(".acmi"):
        args.output += ".acmi"
    return args


def main(argv: List[str]) -> int:
    return run_recording(parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
