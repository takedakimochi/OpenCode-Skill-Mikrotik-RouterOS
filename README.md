# OpenCode-skill-repository

Kumpulan skill untuk agen AI **OpenCode** — kumpulan instruksi (`SKILL.md`)
plus skrip/referensi pendukung yang bisa di-install ke `~/.config/opencode/skills/`.

## Isi Repositori

| Skill | Fungsi |
|---|---|
| [`mikrotik-routeros/`](mikrotik-routeros/SKILL.md) | Skill induk **`mikrotik-kios`**: hanya login ke router MikroTik pribadi (10.10.3.1:8728, user `sistem`) via RouterOS binary API, lalu mendelegasikan semua operasi ke sub-skill `routeros-*`. |
| [`python-virtual-environment/`](python-virtual-environment/SKILL.md) | WAJIB venv sementara di `/tmp/opencode` untuk setiap eksekusi Python/pip agar Python sistem tidak pernah diubah. |

### Sub-skill `routeros-*` (di dalam `mikrotik-routeros/`)

| Sub-skill | Topik |
|---|---|
| `routeros-fundamentals` | Pengetahuan dasar RouterOS 7.x, CLI/REST API, `/ip` `/system` `/interface` |
| `routeros-firewall` | Filter, NAT, mangle, address-list, interface-list |
| `routeros-scripting` | Bahasa scripting RouterOS & file `.rsc` |
| `routeros-hotspot` | Captive portal, walled garden, RADIUS, DHCP option 114 |
| `routeros-container` | Subsystem `/container`, VETH/bridge, device-mode |
| `routeros-app-yaml` | Format YAML `/app` untuk container application (RouterOS 7.21+) |
| `routeros-qemu-chr` | CHR (Cloud Hosted Router) di QEMU — boot, VirtIO, UEFI/SeaBIOS |
| `routeros-quickchr` | Validasi config/script RouterOS against real router via `@tikoci/quickchr` |
| `routeros-netinstall` | Otomasi flashing RouterOS dengan `netinstall-cli`, `.npk`, etherboot |
| `routeros-sniffer` | Capture paket & streaming TZSP ke Wireshark/tshark |
| `routeros-syntax-inspection` | Validasi sintaks via `/console/inspect` & `:parse` |
| `routeros-command-tree` | Introspeksi command tree `/console/inspect` (RAML/OpenAPI) |
| `routeros-mac-telnet` | Protokol MAC-Telnet (UDP 20561), auth MD5 & MTWEI/EC-SRP |
| `routeros-mndp` | MNDP (neighbor discovery) & integrasi `/ip/neighbor` |

Skrip pendukung: [`mikrotik-routeros/scripts/rosapi.py`](mikrotik-routeros/scripts/rosapi.py) — CLI wrapper library `routeros_api` (login otomatis + perintah `status`/`print`/`add`/`set`/`remove`/`exec`), konfigurasi via env `ROS_HOST`, `ROS_PORT`, `ROS_USER`, `ROS_PASS`.

## Instalasi

Salin folder skill ke direktori skill OpenCode:

```bash
# skill induk + sub-skill routeros
cp -r mikrotik-routeros ~/.config/opencode/skills/

# skill python venv
cp -r python-virtual-environment ~/.config/opencode/skills/
```

Library Python untuk skill MikroTik (`routeros_api`) WAJIB di-install di dalam
venv sementara, mengikuti skill `python-virtual-environment` — jangan pernah
`pip install` ke Python global:

```bash
VENV=/tmp/opencode/$(basename "$(pwd)")-venv
python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install routeros_api
```

## Struktur Skill

Setiap skill berupa folder berisi `SKILL.md` (frontmatter `name` + `description`
yang dipakai sebagai pemicu/trigger, lalu isi instruksi) dan opsional:

- `references/` — dokumen detail yang di-load sesuai kebutuhan
- `scripts/` — skrip yang dieksekusi agen

## Catatan

- Repo ini terikat pada router milik owner (kredensial di `mikrotik-routeros/SKILL.md`); jangan dipakai untuk target lain tanpa izin.
- Scope pengetahuan RouterOS: **7.x (long-term ke atas)** — RouterOS v6 tidak dicakup.
