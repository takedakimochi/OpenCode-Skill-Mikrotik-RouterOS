---
name: mikrotik-kios
description: Mengakses/MENJALANKAN PERINTAH pada router MikroTik pribadi milik owner (10.10.3.1:8728, user 'sistem'/'sistem'). Tugas skill ini HANYA login ke router via RouterOS API binary (library Python RouterOS-api) lalu menyerahkan semua operasi ke sub-skill 'routeros-*' di folder yang sama. Use when the user mentions MikroTik, RouterOS, 10.10.3.1, port 8728, user sistem, api mikrotik, kios, perlu login/print/add/set/remove perintah pada router ini. After login, always load the matching routeros-* subskill to execute operations.
---

# MikroTik Router Pribadi (Kios) — LOGIN

Satu-satunya tanggung jawab skill ini: **login ke router owner**. Semua operasi
lain (queue, firewall, scripting, hotspot, container, dsb.) DILARANG ditulis di
sini — untuk apa pun selain login, **load sub-skill `routeros-*` yang sesuai**
(melalui skill tool) sebagai sumber kebenaran, lalu eksekusi lewat sesi API yang
sudah login.

## Data Koneksi (untuk login)

| Parameter | Nilai |
|---|---|
| Host         | `10.10.3.1` |
| RouterOS API | TCP `8728` (protokol biner API, bukan REST/SSH) |
| Username     | `sistem` |
| Password     | `sistem` |
| Library      | `routeros_api` (https://github.com/socialwifi/RouterOS-api) |
| Env override | `ROS_HOST`, `ROS_PORT`, `ROS_USER`, `ROS_PASS` |

Catatan terverifikasi di router ini: hanya port 8728 yang terbuka (SSH/WinBox/www
mati) dan koneksi menerima data non-login dengan balasan `!fatal "not logged in"`.
Pakai API 8728 sebagai satu-satunya kanal.

## Login Wajib (sebelum operasi apa pun)

Jalankan skrip login di bawah ini SETIAP kali akan memakai router. Jangan pernah
mengirim perintah lain sebelum login berhasil.

```bash
python3 ~/.config/opencode/skills/mikrotik-routeros/scripts/rosapi.py status
```

`scripts/rosapi.py` memakai library Python `routeros_api` dan menangani koneksi,
login otomatis (MD5 challenge / plaintext sesuai versi RouterOS), dan parsing
`!re`/`!done`/`!trap`. Bila `status` mengembalikan JSON berisi `identity` →
login berhasil dan sesi siap dipakai.

## Kegagalan Login — Daftar Cek

| Gejala | Penyebab & tindakan |
|---|---|
| `error: timed out` | Router tak reachable / API dimatikan. Cek LAN & `ROS_*`. |
| `[trap] invalid user name or password` | Kredensial salah / user `sistem` dinonaktifkan. |
| `error: connection closed ...` / `!fatal` | Data terkirim sebelum login; selalu login dulu via skrip di atas. |
| `[trap] permission denied` | Hak user `sistem` terbatas; laporkan saja, jangan maksa. |

## Operasi → Pilih Sub-skill routeros-* (WAJIB)

Setelah login sukses, load sub-skill yang sesuai topik, lalu eksekusi operasinya
menggunakan sesi API yang sudah login:

| Operasi | Load sub-skill |
|---|---|
| Sintaks CLI/REST dasar, sistem, versi, `/queue` (bandwidth kios) | `routeros-fundamentals` |
| Firewall filter/NAT/mangle, address-list, interface-list | `routeros-firewall` |
| Skrip `.rsc`, `:local/:foreach`, idempotensi | `routeros-scripting` |
| Hotspot / captive portal / walled-garden | `routeros-hotspot` |
| Container OCI & `/container` VETH | `routeros-container` |
| YAML `/app` (7.22+) | `routeros-app-yaml` |
| Sniffer / TZSP / packet capture | `routeros-sniffer` |
| Neighbor/MNDP discovery | `routeros-mndp` |
| MAC-Telnet (L2 tanpa IP) | `routeros-mac-telnet` |
| Validasi syntax / `:parse` / inspect | `routeros-syntax-inspection`, `routeros-command-tree` |
| CHR/QEMU, quickchr lab | `routeros-qemu-chr`, `routeros-quickchr` |
| Flash via netinstall | `routeros-netinstall` |

Aturan: jangan menulis ulang detail protokol/topik di file ini; untuk apa pun
di luar login, gunakan sub-skill `routeros-*` di atas sebagai sumber kebenaran.

## Keamanan

- Kredensial default plaintext di file skill lokal — jangan commit ke repo
  publik. Gunakan `ROS_*` env bila perlu selain default.
- Mulai read-only (`status`, `print`). `remove`/`exec /system/reboot` = merusak,
  konfirmasi dulu ke owner.
- API 8728 tidak dienkripsi; jangan lewatkan data sensitif.